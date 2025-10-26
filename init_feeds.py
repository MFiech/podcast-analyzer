#!/usr/bin/env python3
"""
Initialize the database with default RSS feeds
"""
from database import PodcastDB

def init_default_feeds():
    """Add default RSS feeds to the database if they don't exist."""
    db = PodcastDB()
    
    default_feeds = []
    
    print("🎙️  Initializing default RSS feeds...")
    
    for feed_data in default_feeds:
        if not db.feed_exists(feed_data["url"]):
            db.add_feed(feed_data["url"], feed_data["title"])
            print(f"✅ Added feed: {feed_data['title']}")
        else:
            print(f"⏭️  Feed already exists: {feed_data['title']}")
    
    print("🎉 Default feeds initialization complete!")

if __name__ == "__main__":
    init_default_feeds()
