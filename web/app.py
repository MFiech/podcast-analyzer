import os
import sys
import markdown
import docker
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import PodcastDB
from tasks import analyze_episode

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

@app.template_filter('markdown')
def markdown_filter(text):
    """Convert markdown text to HTML"""
    return md.convert(text)

@app.route('/')
def index():
    """Main dashboard page, shows all episodes."""
    db = PodcastDB()
    include_hidden = request.args.get('include_hidden', 'false').lower() == 'true'
    episodes = db.list_episodes(include_hidden=include_hidden)
    feeder_status = get_feeder_status()
    return render_template('index.html', episodes=episodes, include_hidden=include_hidden, feeder_status=feeder_status)

@app.route('/episode/<episode_id>')
def episode_detail(episode_id):
    """Shows the details of a single episode."""
    db = PodcastDB()
    episode = db.get_episode_by_id(episode_id)
    if not episode:
        flash('Episode not found!', 'error')
        return redirect(url_for('index'))
    return render_template('episode.html', episode=episode)

@app.route('/data/<path:filename>')
def serve_audio(filename):
    """Serve audio files from the data directory."""
    return send_from_directory('../data', filename)

@app.route('/add', methods=['POST'])
def add_episode():
    """Endpoint to add a new episode."""
    url = request.form.get('url')
    if not url:
        flash('URL is required.', 'error')
        return redirect(url_for('index'))

    try:
        db = PodcastDB()
        if db.episode_exists(url):
            flash('This episode has already been added.', 'info')
        else:
            db.create_placeholder(url, title="Manual Submission")
            analyze_episode.delay(url)
            flash('Episode has been successfully queued for analysis!', 'success')
    except Exception as e:
        flash(f'Error adding episode: {e}', 'error')
        
    return redirect(url_for('index'))

# Episode Management Routes
@app.route('/episode/<episode_id>/hide', methods=['POST'])
def hide_episode(episode_id):
    """Hide an episode from the main view."""
    try:
        db = PodcastDB()
        result = db.hide_episode(episode_id)
        if result.modified_count > 0:
            flash('Episode hidden successfully!', 'success')
        else:
            flash('Episode not found!', 'error')
    except Exception as e:
        flash(f'Error hiding episode: {e}', 'error')
    return redirect(url_for('index'))

@app.route('/episode/<episode_id>/restore', methods=['POST'])
def restore_episode(episode_id):
    """Restore a hidden episode."""
    try:
        db = PodcastDB()
        result = db.restore_episode(episode_id)
        if result.modified_count > 0:
            flash('Episode restored successfully!', 'success')
        else:
            flash('Episode not found!', 'error')
    except Exception as e:
        flash(f'Error restoring episode: {e}', 'error')
    return redirect(url_for('index'))

@app.route('/episode/<episode_id>/retry', methods=['POST'])
def retry_episode(episode_id):
    """Retry a failed episode."""
    try:
        db = PodcastDB()
        result = db.retry_failed_episode(episode_id)
        if result.modified_count > 0:
            # Queue the episode for processing
            episode = db.get_episode_by_id(episode_id)
            if episode:
                analyze_episode.delay(episode['url'])
            flash('Episode queued for retry!', 'success')
        else:
            flash('Episode not found!', 'error')
    except Exception as e:
        flash(f'Error retrying episode: {e}', 'error')
    return redirect(url_for('index'))

@app.route('/episode/<episode_id>/summarize_again', methods=['POST'])
def summarize_again(episode_id):
    """Re-run cleaning and summarization on an existing episode."""
    try:
        db = PodcastDB()
        episode = db.get_episode_by_id(episode_id)
        if not episode:
            flash('Episode not found!', 'error')
            return redirect(url_for('index'))
        
        # Check if episode has raw transcript
        if not episode.get('raw_transcript'):
            flash('No raw transcript available for re-summarization!', 'error')
            return redirect(url_for('episode_detail', episode_id=episode_id))
        
        # Queue the re-summarization task
        from tasks import resummarize_episode
        resummarize_episode.delay(episode_id)
        
        flash('Episode queued for re-summarization!', 'success')
        return redirect(url_for('episode_detail', episode_id=episode_id))
        
    except Exception as e:
        flash(f'Error queuing re-summarization: {e}', 'error')
        return redirect(url_for('episode_detail', episode_id=episode_id))

# RSS Feed Management Routes
@app.route('/feeds')
def manage_feeds():
    """Manage RSS feeds page."""
    db = PodcastDB()
    feeds = db.list_feeds()
    return render_template('feeds.html', feeds=feeds)

@app.route('/feeds/add', methods=['POST'])
def add_feed():
    """Add a new RSS feed."""
    feed_url = request.form.get('feed_url')
    feed_title = request.form.get('feed_title', '')
    
    if not feed_url:
        flash('Feed URL is required.', 'error')
        return redirect(url_for('manage_feeds'))
    
    try:
        db = PodcastDB()
        if db.feed_exists(feed_url):
            flash('This feed has already been added.', 'info')
        else:
            db.add_feed(feed_url, feed_title)
            flash('Feed added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding feed: {e}', 'error')
        
    return redirect(url_for('manage_feeds'))

@app.route('/feeds/<feed_id>/remove', methods=['POST'])
def remove_feed(feed_id):
    """Remove an RSS feed."""
    try:
        db = PodcastDB()
        result = db.remove_feed(feed_id)
        if result.deleted_count > 0:
            flash('Feed removed successfully!', 'success')
        else:
            flash('Feed not found!', 'error')
    except Exception as e:
        flash(f'Error removing feed: {e}', 'error')
    return redirect(url_for('manage_feeds'))

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
