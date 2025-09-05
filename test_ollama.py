#!/usr/bin/env python3
"""
Test Ollama integration
"""
from summarizer import PodcastSummarizer

if __name__ == "__main__":
    summarizer = PodcastSummarizer()
    
    print("Testing Ollama availability...")
    if summarizer.is_ollama_available():
        print("✅ Ollama is running")
        
        # Test summarization with a simple transcript
        test_transcript = """
        Hello everyone, welcome to this podcast episode. Today we're discussing AI and technology.
        Our guest is talking about the future of artificial intelligence and its impact on business.
        They mentioned several companies like OpenAI, Google, and Microsoft.
        Key insights include the importance of data quality and the need for responsible AI development.
        Thank you for listening to our show.
        """
        
        print("\nTesting summarization...")
        summary = summarizer.summarize(test_transcript, "Test Podcast Episode")
        print("Summary generated:")
        print(summary[:500] + "..." if len(summary) > 500 else summary)
    else:
        print("❌ Ollama is not available")