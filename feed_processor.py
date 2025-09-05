#!/usr/bin/env python3
"""
Feed Processor - Fetch and process latest podcast episodes from RSS feeds.
Use this for finding the feeds: https://feedfinder.davidbreder.com/
"""
import feedparser
import click
from dotenv import load_dotenv

# Import the new Celery task
from tasks import analyze_episode
from database import PodcastDB

# Load environment variables from .env file
load_dotenv()

def process_feeds():
    """
    Parses RSS feeds from the database, gets the latest episode from each,
    and processes it.
    """
    click.echo("🎙️  Starting feed processing...")
    db = PodcastDB()
    
    # Get active feeds from database
    feeds = db.list_feeds()
    active_feeds = [feed for feed in feeds if feed.get('active', True)]
    
    if not active_feeds:
        click.echo("❌ No active RSS feeds found in database. Add some feeds first!")
        return
    
    click.echo(f"📡 Found {len(active_feeds)} active feeds to process...")
    
    for feed in active_feeds:
        feed_url = feed['url']
        feed_title = feed.get('title', 'Unknown Feed')
        click.echo(f"\n- Checking feed: {feed_title} ({feed_url})")
        parsed_feed = feedparser.parse(feed_url)
        
        if parsed_feed.bozo:
            click.echo(f"  ❌ Error parsing feed: {parsed_feed.bozo_exception}")
            continue
        
        if 'title' not in parsed_feed.feed:
            click.echo("  ❌ Feed is missing a title.")
            # Try to find a title in the first entry as a fallback
            if parsed_feed.entries and 'title' in parsed_feed.entries[0]:
                 podcast_title = parsed_feed.entries[0].title
            else:
                podcast_title = feed_title
        else:
            podcast_title = parsed_feed.feed.title
            
        click.echo(f"  🎧 Podcast: {podcast_title}")
        
        if not parsed_feed.entries:
            click.echo("  No episodes found in the feed.")
            continue
            
        # The first entry is the latest episode
        latest_episode = parsed_feed.entries[0]
        episode_title = latest_episode.title
        
        # Find the audio URL by looking for an 'enclosure' link with an audio type
        episode_url = None
        for link in latest_episode.get('links', []):
            if link.get('rel') == 'enclosure' and 'audio' in link.get('type', ''):
                episode_url = link.href
                break
        
        # Fallback if no audio enclosure is found
        if not episode_url:
            episode_url = latest_episode.get('link')

        click.echo(f"  📰 Latest Episode: {episode_title}")
        
        if not episode_url:
            click.echo("  ❌ Could not find a valid episode URL in the feed entry.")
            continue
            
        click.echo(f"  🔗 URL: {episode_url}")
        
        # Check if the episode has already been processed before queueing
        if db.episode_exists(episode_url):
            click.echo("  ✅ Episode already in database. Skipping.")
            continue
            
        # Now, create placeholder and queue this episode for processing
        try:
            click.echo("  📝 Creating placeholder in database...")
            db.create_placeholder(episode_url, episode_title)
            click.echo("  ⏳ Queueing episode for analysis...")
            analyze_episode.delay(episode_url)
            click.echo("  👍 Episode successfully queued.")
        except Exception as e:
            click.echo(f"  ❌ Failed to queue episode: {episode_title}")
            click.echo(f"     Error: {e}")

if __name__ == "__main__":
    process_feeds()
