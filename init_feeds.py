#!/usr/bin/env python3
"""
Initialize the database with default RSS feeds
"""
from database import PodcastDB

def init_default_feeds():
    """Add default RSS feeds to the database if they don't exist."""
    db = PodcastDB()
    
    default_feeds = [
        {
            "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCnpBg7yqNauHtlNSpOl5-cg",
            "title": "Peter Yang"
        },
        {
            "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCRYY7IEbkHLH_ScJCu9eWDQ",
            "title": "How I AI"
        },
        {
            "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC6t1O76G0jYXOAoYCm153dA",
            "title": "Lenn's Rachitsky"
        }
    ]
    
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
