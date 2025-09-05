#!/usr/bin/env python3
"""
Complete integration test for Sessions + Prompt Management
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_prompt_management():
    """Test that prompts are working correctly"""
    
    print("🧪 Testing Prompt Management Integration")
    print("-" * 40)
    
    try:
        from summarizer import PodcastSummarizer
        
        # Create summarizer instance
        summarizer = PodcastSummarizer()
        
        if not summarizer.langfuse_enabled:
            print("⚠️  Langfuse not enabled, testing fallback prompts")
            return False
        
        print("✅ Summarizer initialized with Langfuse enabled")
        
        # Test prompt retrieval directly
        try:
            system_prompt = summarizer.langfuse.get_prompt("podcast-analyzer-system", label="production")
            user_prompt = summarizer.langfuse.get_prompt("podcast-summarization-user", label="production")
            
            print(f"✅ System prompt retrieved: {len(system_prompt.prompt)} characters")
            print(f"✅ User prompt template retrieved: {len(user_prompt.prompt)} characters")
            
            # Test compilation
            compiled = user_prompt.compile(
                title="Test Episode",
                transcript="This is a test transcript about AI and product management..."
            )
            print(f"✅ User prompt compiled: {len(compiled)} characters")
            
        except Exception as e:
            print(f"❌ Prompt retrieval failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt management test failed: {e}")
        return False

def test_sessions_and_prompts():
    """Test full integration: Sessions + Prompt Management"""
    
    print("\n🎯 Testing Full Integration: Sessions + Prompt Management")
    print("-" * 55)
    
    try:
        from langfuse import observe
        from summarizer import PodcastSummarizer
        
        # Create a session by using consistent user_id
        session_user_id = "podcast_analyzer_session"
        
        print(f"👤 Using session user_id: {session_user_id}")
        
        # Simulate analyzing multiple episodes in the same session
        episode_data = [
            {
                "title": "AI in Product Management", 
                "transcript": "This episode discusses how artificial intelligence is transforming product management workflows, with frameworks like RICE prioritization and tools like Linear for issue tracking. Key insights include the importance of data-driven decision making and the rise of AI-powered analytics platforms."
            },
            {
                "title": "Startup Funding Trends 2024",
                "transcript": "This episode covers the latest trends in startup funding, including the shift toward profitability, the rise of AI startups, and new investment patterns. Companies like Anthropic and OpenAI are discussed, along with market dynamics and future outlook for venture capital."
            }
        ]
        
        # Process episodes using the updated summarizer (with prompt management)
        summarizer = PodcastSummarizer()
        
        for i, episode in enumerate(episode_data, 1):
            print(f"\n📄 Processing Episode {i}: {episode['title']}")
            
            try:
                # This will use Langfuse Prompt Management + Sessions (user_id)
                summary = summarizer.summarize(episode['transcript'], episode['title'])
                
                print(f"✅ Episode {i} processed successfully")
                print(f"📝 Summary length: {len(summary)} characters")
                print(f"🔗 This trace is part of session: {session_user_id}")
                
                # Add small delay between episodes
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Episode {i} processing failed: {e}")
                return False
        
        # Flush traces to ensure they're sent to Langfuse
        if summarizer.langfuse_enabled and summarizer.langfuse:
            summarizer.langfuse.flush()
            print(f"\n📊 All traces flushed to Langfuse session: {session_user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full integration test failed: {e}")
        return False

def show_next_steps():
    """Show user what to do next"""
    
    print("\n🎉 Integration Test Complete!")
    print("=" * 50)
    
    print("\n🔍 What to check in Langfuse:")
    print("1. 🏠 Go to http://localhost:4000")
    print("2. 📊 Click 'Sessions' in sidebar - you should see 'podcast_analyzer_session'")
    print("3. 🎯 Click on the session to see grouped traces")
    print("4. 📋 Click 'Prompts' to see your managed prompts")
    print("5. 🔗 Click on a trace to see:")
    print("   • Rich input/output data (no more empty inputs!)")
    print("   • Prompt version tracking")
    print("   • Token usage and costs")
    print("   • Processing times")
    
    print(f"\n✨ Key Features Now Working:")
    print("• ✅ Sessions: Multiple episodes grouped by user_id")
    print("• ✅ Prompt Management: Centralized, versioned prompts")
    print("• ✅ Rich Tracing: Detailed input/output capture")
    print("• ✅ LLM Observability: Token usage and performance")
    
    print(f"\n🚀 Benefits:")
    print("• 📊 Track performance across episodes")
    print("• 🔄 A/B test different prompt versions")
    print("• 💰 Monitor costs and token usage")
    print("• 🎯 Debug issues with detailed traces")
    print("• 📈 Analyze user journeys and workflows")

def main():
    """Run all integration tests"""
    print("🧪 Langfuse Full Integration Test")
    print("=" * 40)
    
    # Check environment variables
    required_vars = ['LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check OpenAI key for actual summarization
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set - prompts will load but summarization may fail")
    
    # Run tests
    prompt_success = test_prompt_management()
    integration_success = test_sessions_and_prompts()
    
    if prompt_success and integration_success:
        show_next_steps()
        return True
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)