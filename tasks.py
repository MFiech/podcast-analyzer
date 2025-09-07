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
def analyze_episode(self, url, force=False):
    """
    Main function to process a single podcast episode.
    Now properly traced with Langfuse using context managers!
    """
    
    # Initialize Langfuse with dynamic session ID
    from datetime import datetime
    session_date = datetime.now().strftime("%Y-%m-%d")
    session_id = f"podcast_analyzer_{session_date}"
    
    try:
        from langfuse import Langfuse
        langfuse = Langfuse()
        print(f"🎯 [LANGFUSE] - Using session: {session_id}")
        
        # Use context manager for the main trace with session
        with langfuse.start_as_current_span(
            name="podcast_episode_analysis",
            input={"url": url, "force": force},
            metadata={
                "episode_url": url,
                "force_reprocess": force
            }
        ) as main_span:
            # Set the session ID at the trace level
            main_span.update_trace(
                session_id=session_id,
                user_id="podcast_analyzer",
                tags=["podcast", "analysis", "automated"]
            )
            
            return _analyze_episode_with_tracing(url, force, langfuse, main_span)
        
    except Exception as e:
        print(f"⚠️  [LANGFUSE] - Langfuse setup failed, running without tracing: {e}")
        return _analyze_episode_with_tracing(url, force, None, None)

def _analyze_episode_with_tracing(url, force, langfuse, main_span):
    """Internal function that does the actual work with optional tracing"""
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
            result = {"status": "already_processed", "url": url}
            if main_span:
                main_span.update(output=result)
            return result

        # Step 1: Download
        if langfuse and main_span:
            download_span = langfuse.span(
                name="download_audio",
                input={"url": url},
                metadata={"step": 1},
                trace_id=main_span.trace_id
            )
        
        episode_data = downloader.download(url)
        if not episode_data:
            raise RuntimeError("Failed to download episode")
            
        if langfuse and main_span:
            download_span.end(output={
                "title": episode_data['title'],
                "duration": episode_data.get('duration', 'unknown'),
                "file_path": episode_data['file_path']
            })
            
        # Step 2: Transcribe (or load existing)
        if langfuse and main_span:
            transcribe_span = langfuse.span(
                name="transcribe_audio",
                input={
                    "file_path": episode_data['file_path'],
                    "title": episode_data['title']
                },
                metadata={"step": 2},
                trace_id=main_span.trace_id
            )
        
        transcript_path = transcriber.get_transcript_path(episode_data['title'])
        if transcript_path.exists() and not force:
            raw_transcript = transcript_path.read_text(encoding='utf-8')
            transcribe_method = "loaded_from_cache"
        else:
            raw_transcript = transcriber.transcribe(episode_data['file_path'], episode_data['title'])
            if not raw_transcript:
                raise RuntimeError("Failed to transcribe audio")
            transcribe_method = "whisper_transcription"
                
        episode_data['raw_transcript'] = raw_transcript
        
        if langfuse and main_span:
            transcribe_span.end(output={
                "transcript_length": len(raw_transcript),
                "word_count": len(raw_transcript.split()),
                "method": transcribe_method
            })
        
        # Step 3: Clean transcript with proper tracing
        print("\n🧹 Cleaning transcript...")
        if langfuse and main_span:
            clean_span = langfuse.span(
                name="clean_transcript",
                input={
                    "raw_transcript_length": len(raw_transcript),
                    "title": episode_data['title']
                },
                metadata={"step": 3},
                trace_id=main_span.trace_id
            )
        
        clean_transcript = cleaner.clean_transcript(raw_transcript, episode_data['title'])
        episode_data['transcript'] = clean_transcript
        
        if langfuse and main_span:
            clean_span.end(output={
                "clean_transcript_length": len(clean_transcript),
                "reduction_ratio": f"{len(clean_transcript)/len(raw_transcript)*100:.1f}%"
            })
        
        # Step 4: Summarize with proper trace linking
        print("\n🤖 Generating summary...")
        if langfuse and main_span:
            # Pass the span to summarizer for proper nesting
            summary = summarizer.summarize_with_trace(clean_transcript, episode_data['title'], main_span)
        else:
            # Fallback without tracing
            summary = summarizer.summarize(clean_transcript, episode_data['title'])
            
        episode_data['summary'] = summary
        
        # Step 5: Save to database
        episode_data['status'] = 'completed'
        db.save_episode(episode_data)
        
        # Keep audio file for web playback
        print(f"🎵 Audio file kept for playback: {episode_data['file_path']}")
            
        total_time = time.time() - start_time
        print(f"\n🎉 [TASK SUCCESS] - Analysis complete! Total time: {total_time:.1f}s")
        
        # Finalize the main trace with rich output data
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
        
        if main_span:
            main_span.update(output=result)
            print(f"📊 [LANGFUSE] - Trace completed with session: {session_id}")
        
        # Flush to ensure data is sent
        if langfuse:
            langfuse.flush()
        
        return result
        
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
