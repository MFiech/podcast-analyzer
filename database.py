"""
MongoDB database connection and models
"""
from pymongo import MongoClient
from datetime import datetime
import os

class PodcastDB:
    def __init__(self):
        connection_string = os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO_DB_NAME", "podcast_analyzer")
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.episodes = self.db.episodes
        self.feeds = self.db.feeds
        
    def create_placeholder(self, url, title="", feed_id=None, feed_title=None):
        """Create a placeholder record for a new episode."""
        if self.episode_exists(url):
            return self.get_episode(url)
            
        placeholder = {
            'url': url,
            'title': title,
            'status': 'pending',
            'hidden': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Add feed information if provided
        if feed_id:
            placeholder['feed_id'] = feed_id
        if feed_title:
            placeholder['feed_title'] = feed_title
            
        result = self.episodes.insert_one(placeholder)
        return self.episodes.find_one({'_id': result.inserted_id})

    def save_episode(self, episode_data):
        """Save episode data to database"""
        episode_data['updated_at'] = datetime.utcnow()
        
        # Ensure status is set, default to completed if not specified
        if 'status' not in episode_data:
            episode_data['status'] = 'completed'

        # Check if episode already exists
        existing = self.episodes.find_one({'url': episode_data['url']})
        if existing:
            self.episodes.update_one(
                {'url': episode_data['url']}, 
                {'$set': episode_data}
            )
            return existing['_id']
        else:
            episode_data['created_at'] = datetime.utcnow()
            result = self.episodes.insert_one(episode_data)
            return result.inserted_id
    
    def get_episode(self, url):
        """Get episode by URL"""
        return self.episodes.find_one({'url': url})
    
    def get_episode_by_id(self, episode_id):
        """Get episode by its MongoDB ObjectId."""
        from bson.objectid import ObjectId
        return self.episodes.find_one({'_id': ObjectId(episode_id)})

    def list_episodes(self, include_hidden=False):
        """List all episodes with feed information"""
        query = {}
        if not include_hidden:
            query['hidden'] = {'$ne': True}
        
        # Use aggregation to join with feeds collection
        pipeline = [
            {'$match': query},
            {'$lookup': {
                'from': 'feeds',
                'localField': 'feed_id',
                'foreignField': '_id',
                'as': 'feed_info'
            }},
            {'$addFields': {
                'feed_title': {
                    '$cond': {
                        'if': {'$gt': [{'$size': '$feed_info'}, 0]},
                        'then': {'$arrayElemAt': ['$feed_info.title', 0]},
                        'else': '$feed_title'  # Use stored feed_title if available
                    }
                }
            }},
            {'$sort': {'created_at': -1}}
        ]
        
        return list(self.episodes.aggregate(pipeline))
    
    def update_episode(self, url, update_data):
        """Update episode data"""
        update_data['updated_at'] = datetime.utcnow()
        return self.episodes.update_one(
            {'url': url}, 
            {'$set': update_data}
        )

    def update_episode_status(self, url, status, error_message=None):
        """Update the status of an episode."""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        if error_message:
            update_data['error_message'] = error_message
            
        return self.episodes.update_one(
            {'url': url},
            {'$set': update_data}
        )

    def episode_exists(self, url):
        """Check if an episode with the given URL already exists and is not hidden."""
        return self.episodes.count_documents({"url": url, "hidden": {"$ne": True}}) > 0

    def hide_episode(self, episode_id):
        """Hide an episode from the main view."""
        from bson.objectid import ObjectId
        return self.episodes.update_one(
            {'_id': ObjectId(episode_id)},
            {'$set': {'hidden': True, 'updated_at': datetime.utcnow()}}
        )

    def restore_episode(self, episode_id):
        """Restore a hidden episode."""
        from bson.objectid import ObjectId
        return self.episodes.update_one(
            {'_id': ObjectId(episode_id)},
            {'$set': {'hidden': False, 'restored_at': datetime.utcnow(), 'updated_at': datetime.utcnow()}}
        )

    def retry_failed_episode(self, episode_id):
        """Retry a failed episode by resetting its status to pending."""
        from bson.objectid import ObjectId
        return self.episodes.update_one(
            {'_id': ObjectId(episode_id)},
            {'$set': {'status': 'pending', 'updated_at': datetime.utcnow()}}
        )

    # RSS Feed Management Methods
    def add_feed(self, feed_url, title=""):
        """Add a new RSS feed."""
        if self.feed_exists(feed_url):
            return self.get_feed(feed_url)
            
        feed = {
            'url': feed_url,
            'title': title,
            'active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = self.feeds.insert_one(feed)
        return self.feeds.find_one({'_id': result.inserted_id})

    def get_feed(self, feed_url):
        """Get feed by URL."""
        return self.feeds.find_one({'url': feed_url})

    def get_feed_by_id(self, feed_id):
        """Get feed by its MongoDB ObjectId."""
        from bson.objectid import ObjectId
        return self.feeds.find_one({'_id': ObjectId(feed_id)})

    def list_feeds(self):
        """List all RSS feeds."""
        return list(self.feeds.find().sort('created_at', -1))

    def feed_exists(self, feed_url):
        """Check if a feed with the given URL already exists."""
        return self.feeds.count_documents({"url": feed_url}) > 0

    def remove_feed(self, feed_id):
        """Remove an RSS feed."""
        from bson.objectid import ObjectId
        return self.feeds.delete_one({'_id': ObjectId(feed_id)})

    def update_feed(self, feed_id, update_data):
        """Update feed data."""
        from bson.objectid import ObjectId
        update_data['updated_at'] = datetime.utcnow()
        return self.feeds.update_one(
            {'_id': ObjectId(feed_id)},
            {'$set': update_data}
        )