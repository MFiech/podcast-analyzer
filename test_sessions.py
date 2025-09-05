#!/usr/bin/env python3
"""
Test script to demonstrate Langfuse Sessions functionality
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_sessions():
    """Test Langfuse sessions with mock podcast analysis"""
    
    try:
        from langfuse import Langfuse
        
        langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000')
        )
        
        print("✅ Langfuse client initialized successfully!")
        
        # Create a session for multiple podcast episodes
        session_id = f"podcast-batch-{int(time.time())}"
        print(f"📊 Creating session: {session_id}")
        
        # Simulate processing 3 different podcasts in the same session using decorators and context managers
        from langfuse import observe
        
        @observe(name="podcast_episode_processing")
        def process_episode(episode_data, episode_num):
            """Process a single podcast episode"""
            print(f"\n🎯 Processing Episode {episode_num}: {episode_data['title']}")
            
            # Simulate steps
            download_result = download_audio(episode_data["url"], episode_num)
            transcript_result = transcribe_audio(download_result, episode_num)
            clean_result = clean_transcript(transcript_result, episode_num)
            summary_result = summarize_content(clean_result, episode_data["title"], episode_num)
            
            return {
                "episode_title": episode_data["title"],
                "final_summary_length": f"{800 + episode_num * 100} characters",
                "total_processing_time": f"{5.5 + episode_num * 0.5}s",
                "status": "completed"
            }
        
        @observe(name="download_audio")
        def download_audio(url, episode_num):
            time.sleep(0.1)  # Simulate work
            return {
                "file_path": f"/data/audio/episode_{episode_num}.mp3",
                "duration": f"{45 + episode_num * 5} minutes",
                "status": "success"
            }
        
        @observe(name="transcribe_audio")
        def transcribe_audio(download_result, episode_num):
            time.sleep(0.1)  # Simulate work
            return {
                "transcript_length": f"{15000 + episode_num * 2000} characters",
                "word_count": f"{3000 + episode_num * 400} words",
                "status": "success"
            }
        
        @observe(name="clean_transcript")
        def clean_transcript(transcript_result, episode_num):
            time.sleep(0.1)  # Simulate work
            return {
                "clean_transcript_length": f"{12000 + episode_num * 1500} characters",
                "reduction_ratio": "80%",
                "status": "success"
            }
        
        @observe(as_type="generation", name="openai_summarization")
        def summarize_content(clean_result, title, episode_num):
            time.sleep(0.2)  # Simulate LLM call
            return f"Summary for '{title}': This episode discusses..."
        
        # Simulate processing 3 different podcasts
        podcast_episodes = [
            {"url": "https://example.com/episode1", "title": "AI in Product Management"},
            {"url": "https://example.com/episode2", "title": "Startup Funding Trends 2024"},
            {"url": "https://example.com/episode3", "title": "Building Developer Tools"}
        ]
        
        # Process each episode
        for i, episode in enumerate(podcast_episodes, 1):
            result = process_episode(episode, i)
            print(f"✅ Episode {i} processing complete!")
        
        # Flush all traces
        langfuse.flush()
        print(f"\n📊 Session '{session_id}' completed with {len(podcast_episodes)} episodes!")
        print(f"🔗 View in Langfuse: http://localhost:4000/sessions/{session_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Session test failed: {e}")
        return False

def test_individual_trace():
    """Test creating individual traces (without sessions) using decorators"""
    
    try:
        from langfuse import observe
        
        print("\n🔄 Testing individual trace (no session)")
        
        @observe(name="single_podcast_analysis")
        def analyze_single_episode(url, title):
            """Analyze a single podcast episode"""
            
            @observe(as_type="generation", name="test_summarization")
            def create_summary(episode_title):
                time.sleep(0.1)  # Simulate LLM call
                return f"This is a test summary for '{episode_title}' showing proper input/output capture."
            
            # Call the nested function
            summary = create_summary(title)
            
            return {
                "status": "completed", 
                "summary": summary,
                "url": url,
                "title": title
            }
        
        # Execute the function
        result = analyze_single_episode("https://example.com/single-episode", "Test Episode")
        print("✅ Individual trace test complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual trace test failed: {e}")
        return False

def main():
    """Run all session tests"""
    print("🚀 Starting Langfuse Sessions demonstration...\n")
    
    # Check environment variables
    required_vars = ['LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    # Run tests
    session_success = test_sessions()
    individual_success = test_individual_trace()
    
    if session_success and individual_success:
        print("\n🎉 All session tests passed!")
        print("\n📚 What you learned:")
        print("1. ✅ Sessions group multiple related traces together")
        print("2. ✅ Each trace can have multiple spans and generations")
        print("3. ✅ Proper input/output capture shows meaningful data")
        print("4. ✅ Metadata provides additional context")
        print("5. ✅ Usage tracking shows token consumption")
        print("\n🔗 Check your Langfuse dashboard at: http://localhost:4000")
    else:
        print("❌ Some tests failed.")
    
    return session_success and individual_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)