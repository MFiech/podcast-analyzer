import os
import time
from pathlib import Path

from celery_app import celery_app
from downloader import PodcastDownloader
from transcriber import AudioTranscriber
from cleaner import TranscriptCleaner
from summarizer import PodcastSummarizer
from database import PodcastDB
from langfuse import Langfuse, observe

# Create data directories
DATA_DIR = Path("data")
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
SUMMARIES_DIR = DATA_DIR / "summaries"

def setup_directories():
    """Ensure data directories exist."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)


@celery_app.task(bind=True)
@observe(name="podcast_episode_analysis")
def analyze_episode(self, url, force=False):
    """
    Main function to process a single podcast episode.
    Uses lightweight Langfuse tracing with per-episode sessions.
    """
    return _analyze_episode_with_tracing(url, force)

def _analyze_episode_with_tracing(url, force):
    """Internal function that does the actual work"""
    db = PodcastDB()

    try:
        print(f"🚀 [TASK START] - Analyzing: {url}")
        db.update_episode_status(url, 'processing')
        start_time = time.time()

        setup_directories()

        # Initialize components
        downloader = PodcastDownloader(str(Path("data/audio")))
        transcriber = AudioTranscriber()
        cleaner = TranscriptCleaner()
        summarizer = PodcastSummarizer()

        # Check if the episode has already been fully processed
        episode = db.get_episode(url)
        if not force and episode and episode.get('status') == 'completed':
            print("✅ Episode already processed. Use --force to re-analyze.")
            return {"status": "already_processed", "url": url}

        # Step 1: Download
        # Get the original metadata from placeholder before download
        original_episode = db.get_episode(url)
        original_title = original_episode.get('title', '') if original_episode else ''
        original_feed_id = original_episode.get('feed_id') if original_episode else None
        original_feed_title = original_episode.get('feed_title', '') if original_episode else ''

        episode_data = downloader.download(url)
        if not episode_data:
            raise RuntimeError("Failed to download episode")

        # Preserve the original RSS metadata if it exists (don't use the downloaded file's metadata)
        if original_title:
            episode_data['title'] = original_title
        if original_feed_id:
            episode_data['feed_id'] = original_feed_id
        if original_feed_title:
            episode_data['feed_title'] = original_feed_title

        # Step 2: Transcribe (or load existing)
        transcript_path = transcriber.get_transcript_path(episode_data['title'])
        if transcript_path.exists() and not force:
            raw_transcript = transcript_path.read_text(encoding='utf-8')
            transcribe_method = "loaded_from_cache"
        else:
            raw_transcript = transcriber.transcribe(f"data/{episode_data['file_path']}", episode_data['title'])
            if not raw_transcript:
                raise RuntimeError("Failed to transcribe audio")
            transcribe_method = "whisper_transcription"

        episode_data['raw_transcript'] = raw_transcript

        # Create session ID from sanitized episode title
        sanitized_title = "".join(c for c in episode_data['title'] if c.isalnum() or c in (' ', '_')).rstrip()
        session_id = sanitized_title.replace(' ', '_')[:100]  # Limit to 100 chars

        # Set Langfuse session/trace metadata using official API
        try:
            from langfuse import get_client
            langfuse_client = get_client()
            langfuse_client.update_current_trace(
                session_id=session_id,
                user_id="podcast_analyzer",
                tags=["podcast", "analysis"],
                metadata={
                    "episode_url": url,
                    "episode_title": episode_data['title'],
                    "force_reprocess": force
                }
            )
            print(f"🎯 [LANGFUSE] - Session: {session_id}")
        except Exception as e:
            print(f"⚠️  [LANGFUSE] - Session setup failed: {e}")

        # Step 3: Clean transcript (traced via @observe decorator)
        print("\n🧹 Cleaning transcript...")
        clean_transcript = cleaner.clean_transcript(raw_transcript, episode_data['title'])
        episode_data['transcript'] = clean_transcript

        # Step 4: Summarize (traced via @observe decorator)
        print("\n🤖 Generating summary...")
        # Fetch custom instructions from the feed if available
        custom_instructions = ""
        if episode_data.get('feed_id'):
            feed = db.get_feed_by_id(str(episode_data['feed_id']))
            if feed:
                custom_instructions = feed.get('customPromptInstructions', '')
                if custom_instructions:
                    print(f"📋 Using custom instructions from feed: {feed.get('title', 'Unknown')}")

        summary = summarizer.summarize(clean_transcript, episode_data['title'], custom_instructions=custom_instructions)
        episode_data['summary'] = summary

        episode_data['duration'] = episode_data.get('duration', 0)
        # Step 5: Save to database
        episode_data['status'] = 'completed'
        db.save_episode(episode_data)

        # Keep audio file for web playback
        print(f"🎵 Audio file kept for playback: {episode_data['file_path']}")

        total_time = time.time() - start_time
        print(f"\n🎉 [TASK SUCCESS] - Analysis complete! Total time: {total_time:.1f}s")

        # Return processing result
        result = {
            "episode_title": episode_data['title'],
            "episode_url": url,
            "total_processing_time": f"{total_time:.1f}s",
            "final_summary_length": len(episode_data['summary']),
            "transcript_length": len(episode_data['transcript']),
            "raw_transcript_length": len(episode_data['raw_transcript']),
            "compression_ratio": f"{len(episode_data['summary'])/len(episode_data['transcript'])*100:.1f}%",
            "status": "completed"
        }

        # Flush Langfuse traces to ensure they're sent to cloud
        try:
            from langfuse import get_client
            langfuse_client = get_client()
            langfuse_client.flush()
            print(f"📊 [LANGFUSE] - Observations flushed to cloud")
        except Exception as e:
            print(f"⚠️  [LANGFUSE] - Flush warning: {e}")

        return result

    except Exception as e:
        print(f"❌ [TASK FAILED] - Error analyzing {url}: {e}")
        db.update_episode_status(url, 'failed', error_message=str(e))
        raise

@celery_app.task(bind=True)
def resummarize_episode(self, episode_id):
    """
    Re-run cleaning and summarization on an existing episode using the raw transcript.
    LLM calls are automatically traced via @observe decorators.
    """
    from bson.objectid import ObjectId

    db = PodcastDB()
    try:
        print(f"🔄 [RESUMMARIZE START] - Episode ID: {episode_id}")

        # Get the episode
        episode = db.get_episode_by_id(episode_id)
        if not episode:
            raise RuntimeError("Episode not found")

        if not episode.get('raw_transcript'):
            raise RuntimeError("No raw transcript available for re-summarization")

        # Update status to processing
        db.update_episode_status(episode['url'], 'processing')
        start_time = time.time()

        # Initialize components
        summarizer = PodcastSummarizer()

        # Step 1: Use existing cleaned transcript (no re-cleaning needed)
        print("\n📄 Using existing cleaned transcript...")
        clean_transcript = episode.get('transcript', episode['raw_transcript'])

        # Step 2: Fetch custom instructions from the feed if available
        custom_instructions = ""
        if episode.get('feed_id'):
            feed = db.get_feed_by_id(str(episode['feed_id']))
            if feed:
                custom_instructions = feed.get('customPromptInstructions', '')
                print(f"📋 Using custom instructions from feed: {feed.get('title', 'Unknown')}")

        # Step 3: Generate new summary (traced via @observe)
        print("\n🤖 Re-generating summary...")
        summary = summarizer.summarize(clean_transcript, episode['title'], custom_instructions=custom_instructions)

        # Step 4: Update the episode with new summary
        update_data = {
            'transcript': clean_transcript,
            'summary': summary,
            'status': 'completed',
            'updated_at': time.time()
        }

        db.update_episode(episode['url'], update_data)

        total_time = time.time() - start_time
        print(f"\n🎉 [RESUMMARIZE SUCCESS] - Re-summarization complete! Total time: {total_time:.1f}s")

        # Flush Langfuse traces to ensure they're sent to cloud
        try:
            from langfuse import get_client
            langfuse_client = get_client()
            langfuse_client.flush()
            print(f"📊 [LANGFUSE] - Observations flushed to cloud")
        except Exception as flush_error:
            print(f"⚠️  [LANGFUSE] - Flush warning: {flush_error}")

    except Exception as e:
        print(f"❌ [RESUMMARIZE FAILED] - Error re-summarizing episode {episode_id}: {e}")
        if episode:
            db.update_episode_status(episode['url'], 'failed', error_message=str(e))
        raise

@celery_app.task(bind=True)
def reclean_episode(self, episode_id):
    """
    Re-clean the raw transcript and re-summarize an existing episode.
    Does NOT re-download or re-transcribe.
    LLM calls are automatically traced via @observe decorators.
    """
    from bson.objectid import ObjectId

    db = PodcastDB()
    episode = None
    try:
        print(f"🔄 [RECLEAN START] - Episode ID: {episode_id}")

        # Get the episode
        episode = db.get_episode_by_id(episode_id)
        if not episode:
            raise RuntimeError("Episode not found")

        if not episode.get('raw_transcript'):
            raise RuntimeError("No raw transcript available for re-cleaning")

        # Update status to processing
        db.update_episode_status(episode['url'], 'processing')
        start_time = time.time()

        # Initialize components
        cleaner = TranscriptCleaner()
        summarizer = PodcastSummarizer()

        # Step 1: Re-clean the raw transcript (traced via @observe)
        print("\n🧹 Re-cleaning transcript...")
        clean_transcript = cleaner.clean_transcript(episode['raw_transcript'], episode['title'])

        # Step 2: Fetch custom instructions from the feed if available
        custom_instructions = ""
        if episode.get('feed_id'):
            feed = db.get_feed_by_id(str(episode['feed_id']))
            if feed:
                custom_instructions = feed.get('customPromptInstructions', '')
                print(f"📋 Using custom instructions from feed: {feed.get('title', 'Unknown')}")

        # Step 3: Generate new summary (traced via @observe)
        print("\n🤖 Re-generating summary...")
        summary = summarizer.summarize(clean_transcript, episode['title'], custom_instructions=custom_instructions)

        # Step 4: Update the episode with new cleaned transcript and summary
        update_data = {
            'transcript': clean_transcript,
            'summary': summary,
            'status': 'completed',
            'updated_at': time.time()
        }

        db.update_episode(episode['url'], update_data)

        total_time = time.time() - start_time
        print(f"\n🎉 [RECLEAN SUCCESS] - Re-cleaning and summarization complete! Total time: {total_time:.1f}s")

        # Flush Langfuse traces to ensure they're sent to cloud
        try:
            from langfuse import get_client
            langfuse_client = get_client()
            langfuse_client.flush()
            print(f"📊 [LANGFUSE] - Observations flushed to cloud")
        except Exception as flush_error:
            print(f"⚠️  [LANGFUSE] - Flush warning: {flush_error}")

    except Exception as e:
        print(f"❌ [RECLEAN FAILED] - Error re-cleaning episode {episode_id}: {e}")
        if episode:
            db.update_episode_status(episode['url'], 'failed', error_message=str(e))
        raise
