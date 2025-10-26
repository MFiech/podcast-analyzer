#!/usr/bin/env python3
"""
Scheduled Feed Processor - Automatically process RSS feeds on a schedule.
Runs the feed processor every hour (configurable via FEEDER_INTERVAL_MINUTES).
"""
import os
import sys
import signal
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the feed processor and database
from feed_processor import process_feeds
from init_feeds import init_default_feeds
from database import PodcastDB

# Configuration
FEEDER_INTERVAL_MINUTES = int(os.getenv('FEEDER_INTERVAL_MINUTES', '60'))

# Create scheduler
scheduler = BlockingScheduler()

def log_message(message):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def scheduled_feed_processing():
    """Wrapper function for scheduled feed processing."""
    db = PodcastDB()
    log_message("🔄 Starting scheduled feed processing...")

    # Mark as running
    db.update_feeder_status(is_running=True)

    try:
        process_feeds()
        # Mark as completed successfully
        db.update_feeder_status(is_running=False, status='success')
        log_message("✅ Feed processing completed successfully")
    except Exception as e:
        # Mark as failed
        db.update_feeder_status(is_running=False, status='failed', error_message=str(e))
        log_message(f"❌ Error during feed processing: {e}")
        # Continue running even if there's an error

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    log_message("🛑 Received shutdown signal, stopping scheduler...")
    scheduler.shutdown()
    sys.exit(0)

def main():
    """Main function to set up and run the scheduled feeder."""
    log_message("🚀 Starting Scheduled Feed Processor")
    log_message(f"⏰ Interval: Every {FEEDER_INTERVAL_MINUTES} minutes")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Initialize default feeds on startup
    log_message("📋 Initializing default feeds...")
    try:
        init_default_feeds()
    except Exception as e:
        log_message(f"⚠️  Warning: Failed to initialize feeds: {e}")

    # Run feed processing immediately on startup
    log_message("🎬 Running initial feed processing...")
    scheduled_feed_processing()

    # Schedule the feed processing task
    scheduler.add_job(
        scheduled_feed_processing,
        trigger=IntervalTrigger(minutes=FEEDER_INTERVAL_MINUTES),
        id='feed_processor',
        name='Process RSS Feeds',
        replace_existing=True
    )

    log_message(f"✅ Scheduler started. Next run in {FEEDER_INTERVAL_MINUTES} minutes")
    log_message("📊 Monitor logs at http://localhost:5000 (Dozzle)")

    try:
        # Start the scheduler (blocking)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log_message("🛑 Scheduler stopped")

if __name__ == "__main__":
    main()
