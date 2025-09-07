#!/usr/bin/env python3
"""
Test the new Langfuse tracing implementation
WARNING: This test DOES create real traces in Langfuse - use test_sessions.py for safe testing
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_new_tracing():
    """Test the new manual trace management approach"""
    
    print("🧪 Testing New Langfuse Tracing Implementation")
    print("=" * 50)
    
    try:
        from langfuse import Langfuse
        from summarizer import PodcastSummarizer
        
        # Initialize Langfuse
        langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000')
        )
        
        print("✅ Langfuse client initialized")
        
        # Create a test trace with session
        session_id = "test_session_" + str(int(time.time()))
        main_trace = langfuse.trace(
            name="test_podcast_analysis",
            session_id=session_id,
            input={"url": "https://test.com/episode", "force": False},
            metadata={
                "test": True,
                "timestamp": time.time()
            }
        )
        
        print(f"✅ Created trace with session: {session_id}")
        
        # Test nested spans
        download_span = main_trace.span(
            name="test_download",
            input={"url": "https://test.com/episode"},
            metadata={"step": 1}
        )
        
        time.sleep(0.1)  # Simulate work
        
        download_span.end(output={
            "title": "Test Episode",
            "duration": "30 minutes",
            "file_path": "/test/audio/episode.mp3"
        })
        
        print("✅ Download span completed")
        
        # Test transcription span
        transcribe_span = main_trace.span(
            name="test_transcribe",
            input={"file_path": "/test/audio/episode.mp3"},
            metadata={"step": 2}
        )
        
        time.sleep(0.1)  # Simulate work
        
        transcribe_span.end(output={
            "transcript_length": 5000,
            "word_count": 1000,
            "method": "whisper_transcription"
        })
        
        print("✅ Transcribe span completed")
        
        # Test cleaning span
        clean_span = main_trace.span(
            name="test_clean",
            input={"raw_transcript_length": 5000},
            metadata={"step": 3}
        )
        
        time.sleep(0.1)  # Simulate work
        
        clean_span.end(output={
            "clean_transcript_length": 4000,
            "reduction_ratio": "80.0%"
        })
        
        print("✅ Clean span completed")
        
        # Test generation (LLM call simulation)
        generation = langfuse.generation(
            name="test_openai_summarization",
            model="gpt-4o-mini",
            input={
                "transcript_length": 4000,
                "title": "Test Episode",
                "prompt_source": "langfuse_managed"
            },
            metadata={
                "step": 4,
                "temperature": 0.7,
                "max_tokens": 2000
            },
            trace_id=main_trace.id
        )
        
        time.sleep(0.2)  # Simulate LLM call
        
        generation.end(
            output={
                "summary": "This is a test summary of the episode content...",
                "summary_length": 150,
                "compression_ratio": "3.75%"
            },
            usage={
                "input": 1000,
                "output": 50,
                "total": 1050
            }
        )
        
        print("✅ Generation completed with token usage")
        
        # Finalize main trace
        main_trace.end(output={
            "episode_title": "Test Episode",
            "total_processing_time": "0.5s",
            "status": "completed"
        })
        
        print("✅ Main trace completed")
        
        # Flush to Langfuse
        langfuse.flush()
        
        print(f"\n🎉 Test completed successfully!")
        print(f"📊 Check your Langfuse dashboard:")
        print(f"   • Sessions: http://localhost:4000/sessions")
        print(f"   • Look for session: {session_id}")
        print(f"   • Traces: http://localhost:4000/traces")
        print(f"   • Generations: http://localhost:4000/generations")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the tracing test"""
    
    # Check environment variables
    required_vars = ['LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    success = test_new_tracing()
    
    if success:
        print("\n📋 What you should see in Langfuse:")
        print("1. Go to Sessions → find your test session")
        print("2. Click on it to see the full trace hierarchy:")
        print("   └── test_podcast_analysis (main trace)")
        print("       ├── test_download (span)")
        print("       ├── test_transcribe (span)")  
        print("       ├── test_clean (span)")
        print("       └── test_openai_summarization (generation)")
        print("3. Each step should have rich input/output data")
        print("4. The generation should show token usage")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)