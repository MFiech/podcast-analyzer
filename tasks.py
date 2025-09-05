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

@observe(name="clean_transcript") 
def clean_with_langfuse_trace(raw_transcript, title, cleaner):
    """Clean transcript with proper Langfuse tracing"""
    return cleaner.clean_transcript(raw_transcript, title)

@celery_app.task(bind=True)
@observe(name="podcast_episode_analysis")
def analyze_episode(self, url, force=False):
    """
    Main function to process a single podcast episode.
    Now properly traced with Langfuse!
    """
    db = PodcastDB()
    
    try:
        print(f"🚀 [TASK START] - Analyzing: {url}")
        print(f"📊 [LANGFUSE] - This episode will be traced as: podcast_episode_analysis")
        
        # Set up session tracking for this episode
        session_id = "podcast_analyzer_session"
        try:
            from langfuse import Langfuse
            langfuse = Langfuse()
            langfuse.update_current_trace(session_id=session_id)
            print(f"🎯 [LANGFUSE] - Added to session: {session_id}")
        except Exception as e:
            print(f"⚠️  [LANGFUSE] - Session setup failed: {e}")
        
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
        episode_data = downloader.download(url)
        if not episode_data:
            raise RuntimeError("Failed to download episode")
            
        # Step 2: Transcribe (or load existing)
        transcript_path = transcriber.get_transcript_path(episode_data['title'])
        if transcript_path.exists() and not force:
            raw_transcript = transcript_path.read_text(encoding='utf-8')
        else:
            raw_transcript = transcriber.transcribe(episode_data['file_path'], episode_data['title'])
            if not raw_transcript:
                raise RuntimeError("Failed to transcribe audio")
                
        episode_data['raw_transcript'] = raw_transcript
        
        # Step 3: Clean (now properly traced)
        print("\n🧹 Cleaning transcript...")
        clean_transcript = clean_with_langfuse_trace(raw_transcript, episode_data['title'], cleaner)
        episode_data['transcript'] = clean_transcript
        
        # Step 4: Summarize (already traced in the summarizer class)
        print("\n🤖 Generating summary...")
        summary = summarizer.summarize(clean_transcript, episode_data['title'])
        episode_data['summary'] = summary
        
        # Step 5: Save to database
        episode_data['status'] = 'completed'
        db.save_episode(episode_data)
        
        # Keep audio file for web playback
        print(f"🎵 Audio file kept for playback: {episode_data['file_path']}")
            
        total_time = time.time() - start_time
        print(f"\n🎉 [TASK SUCCESS] - Analysis complete! Total time: {total_time:.1f}s")
        print(f"📊 [LANGFUSE] - Trace completed with rich input/output data")
        
        # Return structured result for Langfuse observation
        return {
            "episode_title": episode_data['title'],
            "episode_url": url,
            "total_processing_time": f"{total_time:.1f}s",
            "final_summary_length": len(episode_data['summary']),
            "transcript_length": len(episode_data['transcript']),
            "raw_transcript_length": len(episode_data['raw_transcript']),
            "compression_ratio": f"{len(episode_data['summary'])/len(episode_data['transcript'])*100:.1f}%",
            "status": "completed"
        }
        
    except Exception as e:
        print(f"❌ [TASK FAILED] - Error analyzing {url}: {e}")
        db.update_episode_status(url, 'failed', error_message=str(e))
        # Optional: re-raise the exception if you want Celery to record it as a failure
        raise

@celery_app.task(bind=True)
@observe(as_type="span", name="podcast_episode_resummarization")
def resummarize_episode(self, episode_id):
    """
    Re-run cleaning and summarization on an existing episode using the raw transcript.
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
        
        # Add metadata to the trace
        try:
            from langfuse.decorators import LangfuseDecorator
            # Metadata will be added through the @observe decorator
        except ImportError:
            pass  # Langfuse not available
        
        # Initialize components
        cleaner = TranscriptCleaner()
        summarizer = PodcastSummarizer()
        
        # Step 1: Clean the raw transcript again
        print("\n🧹 Re-cleaning transcript...")
        clean_transcript = cleaner.clean_transcript(episode['raw_transcript'], episode['title'])
        
        # Step 2: Generate new summary
        print("\n🤖 Re-generating summary...")
        summary = summarizer.summarize(clean_transcript, episode['title'])
        
        # Step 3: Update the episode with new cleaned transcript and summary
        update_data = {
            'transcript': clean_transcript,
            'summary': summary,
            'status': 'completed',
            'updated_at': time.time()
        }
        
        db.update_episode(episode['url'], update_data)
        
        total_time = time.time() - start_time
        print(f"\n🎉 [RESUMMARIZE SUCCESS] - Re-summarization complete! Total time: {total_time:.1f}s")
        
    except Exception as e:
        print(f"❌ [RESUMMARIZE FAILED] - Error re-summarizing episode {episode_id}: {e}")
        if episode:
            db.update_episode_status(episode['url'], 'failed', error_message=str(e))
        raise
