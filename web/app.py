import os
import sys
import markdown
import docker
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import PodcastDB
from tasks import analyze_episode

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Enable CORS for frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [r"http://localhost:*", r"http://127.0.0.1:*", r"http://*:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    },
    r"/data/*": {
        "origins": [r"http://localhost:*", r"http://127.0.0.1:*", r"http://*:*"],
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure markdown
md = markdown.Markdown(extensions=['extra', 'codehilite'])

# Docker client
docker_client = docker.from_env()

def get_feeder_status():
    """Get the status of the feeder container."""
    try:
        container = docker_client.containers.get('podcast_feeder')
        if container.status == 'running':
            return 'running'
        elif container.status in ['exited', 'stopped']:
            # Check if it exited recently (within last 5 minutes) - consider it as "just ran"
            import time
            container_info = container.attrs
            finished_at = container_info['State'].get('FinishedAt')
            if finished_at and finished_at != '0001-01-01T00:00:00Z':
                from datetime import datetime
                finished_time = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
                time_diff = time.time() - finished_time.timestamp()
                if time_diff < 300:  # 5 minutes
                    return 'recently_ran'
            return 'stopped'
        else:
            return container.status
    except docker.errors.NotFound:
        return 'not_found'
    except Exception as e:
        print(f"Error checking feeder status: {e}")
        return 'error'

def start_feeder():
    """Start the feeder container."""
    try:
        container = docker_client.containers.get('podcast_feeder')
        if container.status != 'running':
            container.start()
            return True, "Feeder started successfully"
        else:
            return False, "Feeder is already running"
    except docker.errors.NotFound:
        return False, "Feeder container not found"
    except Exception as e:
        return False, f"Error starting feeder: {e}"

def stop_feeder():
    """Stop the feeder container."""
    try:
        container = docker_client.containers.get('podcast_feeder')
        if container.status == 'running':
            container.stop()
            return True, "Feeder stopped successfully"
        else:
            return False, "Feeder is not running"
    except docker.errors.NotFound:
        return False, "Feeder container not found"
    except Exception as e:
        return False, f"Error stopping feeder: {e}"

def restart_feeder():
    """Restart the feeder container to trigger immediate feed processing."""
    try:
        container = docker_client.containers.get('podcast_feeder')
        container.restart()
        return True, "Feeder restarted - checking for new episodes"
    except docker.errors.NotFound:
        return False, "Feeder container not found"
    except Exception as e:
        return False, f"Error restarting feeder: {e}"

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200

@app.route('/data/<path:filename>')
def serve_audio(filename):
    """Serve audio files from the data directory."""
    return send_from_directory('../data', filename)

# Episode Management JSON API Endpoints
@app.route('/api/episodes/<episode_id>/hide', methods=['POST'])
def api_hide_episode(episode_id):
    """API endpoint to hide an episode."""
    db = PodcastDB()
    try:
        result = db.hide_episode(episode_id)
        if result.modified_count > 0:
            return app.response_class(
                response=dumps({'success': True, 'message': 'Episode hidden'}),
                status=200,
                mimetype='application/json'
            )
        else:
            return app.response_class(
                response=dumps({'error': 'Episode not found'}),
                status=404,
                mimetype='application/json'
            )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/episodes/<episode_id>/restore', methods=['POST'])
def api_restore_episode(episode_id):
    """API endpoint to restore a hidden episode."""
    db = PodcastDB()
    try:
        result = db.restore_episode(episode_id)
        if result.modified_count > 0:
            return app.response_class(
                response=dumps({'success': True, 'message': 'Episode restored'}),
                status=200,
                mimetype='application/json'
            )
        else:
            return app.response_class(
                response=dumps({'error': 'Episode not found'}),
                status=404,
                mimetype='application/json'
            )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/episodes/<episode_id>/retry', methods=['POST'])
def api_retry_episode(episode_id):
    """API endpoint to retry a failed episode."""
    db = PodcastDB()
    try:
        result = db.retry_failed_episode(episode_id)
        if result.modified_count > 0:
            episode = db.get_episode_by_id(episode_id)
            if episode:
                analyze_episode.delay(episode['url'])
            return app.response_class(
                response=dumps({'success': True, 'message': 'Episode queued for retry'}),
                status=200,
                mimetype='application/json'
            )
        else:
            return app.response_class(
                response=dumps({'error': 'Episode not found'}),
                status=404,
                mimetype='application/json'
            )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

# Feeder Container Control Routes
@app.route('/api/feeder/status')
def feeder_status_api():
    """API endpoint to get feeder container status and last run information."""
    from datetime import datetime, timezone

    # Get Docker container status
    container_status = get_feeder_status()

    # Get database feeder status
    db = PodcastDB()
    feeder_data = db.get_feeder_status()

    response = {
        'status': container_status,
        'is_running': feeder_data.get('is_running', False),
        'last_run_status': feeder_data.get('last_run_status', 'never_run'),
        'last_run_time': None,
        'last_run_time_readable': None,
        'next_run_in_minutes': None
    }

    # Calculate last run time info
    last_run_time = feeder_data.get('last_run_time')
    if last_run_time:
        response['last_run_time'] = last_run_time.isoformat()

        # Calculate time ago in human-readable format
        now = datetime.now(timezone.utc)
        if last_run_time.tzinfo is None:
            last_run_time = last_run_time.replace(tzinfo=timezone.utc)

        time_diff = now - last_run_time
        minutes_ago = int(time_diff.total_seconds() / 60)
        hours_ago = int(minutes_ago / 60)

        if minutes_ago < 1:
            response['last_run_time_readable'] = 'Just now'
        elif minutes_ago < 60:
            response['last_run_time_readable'] = f'{minutes_ago} minute{"s" if minutes_ago != 1 else ""} ago'
        elif hours_ago < 24:
            response['last_run_time_readable'] = f'{hours_ago} hour{"s" if hours_ago != 1 else ""} ago'
        else:
            days_ago = int(hours_ago / 24)
            response['last_run_time_readable'] = f'{days_ago} day{"s" if days_ago != 1 else ""} ago'

        # Calculate next run time (assuming hourly schedule)
        interval_minutes = int(os.getenv('FEEDER_INTERVAL_MINUTES', '60'))
        minutes_since_last_run = int(time_diff.total_seconds() / 60)
        next_run_minutes = interval_minutes - minutes_since_last_run
        if next_run_minutes > 0:
            response['next_run_in_minutes'] = next_run_minutes

    return jsonify(response)

@app.route('/api/feeder/start', methods=['POST'])
def start_feeder_api():
    """API endpoint to start the feeder container."""
    success, message = start_feeder()
    return jsonify({'success': success, 'message': message})

@app.route('/api/feeder/stop', methods=['POST'])
def stop_feeder_api():
    """API endpoint to stop the feeder container."""
    success, message = stop_feeder()
    return jsonify({'success': success, 'message': message})

@app.route('/api/feeder/restart', methods=['POST'])
def restart_feeder_api():
    """API endpoint to restart the feeder container and trigger immediate feed processing."""
    success, message = restart_feeder()
    return jsonify({'success': success, 'message': message})

# JSON API Endpoints for Frontend
@app.route('/api/episodes', methods=['GET'])
def api_episodes():
    """API endpoint to get episodes list."""
    db = PodcastDB()
    status_filter = request.args.get('status')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    episodes = db.list_episodes(include_hidden=False)
    
    # Filter by status if provided
    if status_filter:
        episodes = [ep for ep in episodes if ep.get('status') == status_filter]
    
    # Calculate totals
    total = len(episodes)
    completed_count = len([ep for ep in episodes if ep.get('status') == 'completed'])
    processing_count = len([ep for ep in episodes if ep.get('status') in ['pending', 'processing']])
    
    # Apply pagination
    paginated = episodes[offset:offset + limit]
    
    # Convert ObjectId to string for JSON serialization
    for ep in paginated:
        ep['id'] = str(ep['_id'])
        ep.pop('_id', None)
        ep.pop('feed_info', None)  # Remove aggregation field
        # Convert any remaining ObjectId fields
        if 'feed_id' in ep and isinstance(ep['feed_id'], ObjectId):
            ep['feed_id'] = str(ep['feed_id'])
    
    # Use bson.json_util to serialize the response
    return app.response_class(
        response=dumps({'episodes': paginated, 'total': total, 'completed_count': completed_count, 'processing_count': processing_count}),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/episodes/<episode_id>', methods=['GET'])
def api_episode_detail(episode_id):
    """API endpoint to get a single episode."""
    db = PodcastDB()
    try:
        episode = db.get_episode_by_id(episode_id)
        if not episode:
            return jsonify({'error': 'Episode not found'}), 404
        
        episode['id'] = str(episode['_id'])
        episode.pop('_id', None)
        
        # Convert any remaining ObjectId fields
        if 'feed_id' in episode and isinstance(episode['feed_id'], ObjectId):
            episode['feed_id'] = str(episode['feed_id'])
        
        # Use bson.json_util to serialize the response
        return app.response_class(
            response=dumps(episode),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )

@app.route('/api/episodes', methods=['POST'])
def api_add_episode():
    """API endpoint to add a new episode."""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return app.response_class(
            response=dumps({'error': 'URL is required'}),
            status=400,
            mimetype='application/json'
        )
    
    try:
        db = PodcastDB()
        if db.episode_exists(url):
            return app.response_class(
                response=dumps({'error': 'Episode already exists'}),
                status=409,
                mimetype='application/json'
            )
        
        db.create_placeholder(url, title="Manual Submission")
        analyze_episode.delay(url)
        return app.response_class(
            response=dumps({'success': True, 'message': 'Episode queued for analysis'}),
            status=201,
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/episodes/<episode_id>/summarize-again', methods=['POST'])
def api_summarize_again(episode_id):
    """API endpoint to re-summarize an episode."""
    db = PodcastDB()
    try:
        episode = db.get_episode_by_id(episode_id)
        if not episode:
            return app.response_class(
                response=dumps({'error': 'Episode not found'}),
                status=404,
                mimetype='application/json'
            )
        
        if not episode.get('raw_transcript'):
            return app.response_class(
                response=dumps({'error': 'No raw transcript available'}),
                status=400,
                mimetype='application/json'
            )
        
        from tasks import resummarize_episode
        resummarize_episode.delay(episode_id)
        return app.response_class(
            response=dumps({'success': True, 'message': 'Episode queued for re-summarization'}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

# RSS Feeds API Endpoints
@app.route('/api/feeds', methods=['GET'])
def api_feeds():
    """API endpoint to get all feeds."""
    db = PodcastDB()
    feeds = db.list_feeds()
    
    # Convert ObjectId to string and add episode count
    for feed in feeds:
        feed['id'] = str(feed['_id'])
        feed.pop('_id', None)
        
        # Count episodes for this feed
        episodes_count = db.episodes.count_documents({'feed_id': ObjectId(feed['id'])})
        feed['episode_count'] = episodes_count
    
    return app.response_class(
        response=dumps(feeds),
        status=200,
        mimetype='application/json'
    )

@app.route('/api/feeds', methods=['POST'])
def api_add_feed():
    """API endpoint to add a new RSS feed."""
    data = request.get_json()
    feed_url = data.get('feed_url')
    feed_title = data.get('feed_title', '')
    custom_prompt = data.get('custom_prompt', '')
    
    if not feed_url:
        return app.response_class(
            response=dumps({'error': 'Feed URL is required'}),
            status=400,
            mimetype='application/json'
        )
    
    try:
        db = PodcastDB()
        if db.feed_exists(feed_url):
            return app.response_class(
                response=dumps({'error': 'Feed already exists'}),
                status=409,
                mimetype='application/json'
            )
        
        feed = db.add_feed(feed_url, feed_title, custom_prompt)
        feed['id'] = str(feed['_id'])
        feed.pop('_id', None)
        feed['episode_count'] = 0
        return app.response_class(
            response=dumps(feed),
            status=201,
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/feeds/<feed_id>', methods=['PUT'])
def api_update_feed(feed_id):
    """API endpoint to update a feed."""
    db = PodcastDB()
    data = request.get_json()
    print(f"DEBUG: Received data: {data}")
    
    try:
        update_data = {
            'title': data.get('feed_title', ''),
            'url': data.get('feed_url'),
            'customPromptInstructions': data.get('custom_prompt', '')
        }
        print(f"DEBUG: Update data: {update_data}")
        result = db.update_feed(feed_id, update_data)
        
        if result.modified_count == 0:
            return app.response_class(
                response=dumps({'error': 'Feed not found'}),
                status=404,
                mimetype='application/json'
            )
        
        feed = db.get_feed_by_id(feed_id)
        feed['id'] = str(feed['_id'])
        feed.pop('_id', None)
        feed['episode_count'] = db.episodes.count_documents({'feed_id': ObjectId(feed_id)})
        return app.response_class(
            response=dumps(feed),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/api/feeds/<feed_id>', methods=['DELETE'])
def api_delete_feed(feed_id):
    """API endpoint to delete a feed."""
    db = PodcastDB()
    try:
        result = db.remove_feed(feed_id)
        if result.deleted_count == 0:
            return app.response_class(
                response=dumps({'error': 'Feed not found'}),
                status=404,
                mimetype='application/json'
            )
        return app.response_class(
            response=dumps({'success': True, 'message': 'Feed deleted'}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=dumps({'error': str(e)}),
            status=500,
            mimetype='application/json'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
