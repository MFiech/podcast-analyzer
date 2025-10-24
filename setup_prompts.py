#!/usr/bin/env python3
"""
Script to create and manage prompts in Langfuse for podcast summarization
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def create_podcast_prompts():
    """Create prompts for podcast summarization in Langfuse"""
    
    try:
        from langfuse import Langfuse
        
        langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000')
        )
        
        print("🚀 Creating Langfuse prompts for podcast summarization...")

        # 1. Transcript Cleaner System Prompt
        cleaner_system_prompt = langfuse.create_prompt(
            name="podcast-transcript-cleaner-system",
            prompt="""You are a professional transcript cleaner.
Your task is to remove filler words (um, ah, like, you know, etc.)
and small-talk fluff while preserving all technical, business, and conversational content.
Do not shorten or summarize — keep the transcript length and meaning intact.""",
            labels=["production", "podcast", "cleaner", "system"],
            type="text"
        )
        print("✅ Created cleaner system prompt: podcast-transcript-cleaner-system")

        # 2. Transcript Cleaner User Prompt Template
        cleaner_user_prompt = langfuse.create_prompt(
            name="podcast-transcript-cleaner-user",
            prompt="""Clean the following podcast transcript while preserving all content.
Keep the same length, remove fillers and irrelevant small-talk,
and make sure technical/business details remain untouched.

Transcript:
{{raw_transcript}}""",
            labels=["production", "podcast", "cleaner", "user"],
            type="text"
        )
        print("✅ Created cleaner user prompt: podcast-transcript-cleaner-user")

        # 3. Summarizer System Prompt
        system_prompt = langfuse.create_prompt(
            name="podcast-analyzer-system",
            prompt="""You are a professional podcast analyst. 
Your job is to create structured summaries of cleaned podcast transcripts. 
Your summaries must adapt to the type of content:

1. If the episode is about PRODUCT MANAGEMENT, AI, TOOLS, or OPERATIONS:
   - Focus on frameworks, methodologies, tools/tech stacks, and clear product/AI insights.
   - Summarize in a way that helps a product manager learn and stay up to date.
   - Provide external links if frameworks/methods are only partially explained.
   - Strip out anecdotes and irrelevant chatter.
   - Leadership lessons only if they are the explicit theme.

2. If the episode is about STRATEGY, STARTUPS, VC, or MARKET TRENDS:
   - Focus on industry insights, investment theses, emerging trends, and market dynamics.
   - Capture the essence of strategic discussions and ecosystem shifts.
   - Provide context on why the trend matters and where to explore further (reports, articles, companies).
   - Do not attempt product/AI tooling detail unless explicitly discussed.

Across all types:
- Provide two layers of summary: quick TL;DR and detailed notes.
- Avoid prescriptive "to-dos" for the user.
- Quotes should be concise and memorable.
- Companies/people should always be noted with context.""",
            labels=["production", "podcast", "system"],
            type="text"
        )
        print("✅ Created summarizer system prompt: podcast-analyzer-system")

        # 4. Summarizer User Prompt Template
        user_prompt = langfuse.create_prompt(
            name="podcast-summarization-user",
            prompt="""Please analyze this podcast transcript and produce a structured summary with two layers:

---

**TL;DR (quick read):**

• 3–5 bullets summarizing the main takeaways (~100 words max)

---

**Detailed Notes:**

**Title:** {{title}}

**Overview:**
2–3 sentences on the core theme and relevance.

**Key Topics:**

• [Main topic 1]
• [Main topic 2]

IF PRODUCT/AI/OPERATIONAL:
  **Frameworks & Methodologies:**
  
  • [Framework/method: explanation or link if vague]

  **Tools & Tech Stacks:**
  
  • [Tool/tech: context of use]

  **Key Insights:**
  
  • [Insight phrased for product/AI relevance]

IF STRATEGY/VC/TRENDS:
  **Market & Strategic Insights:**
  
  • [Trend/insight: why it matters]

  **Investment/Startup Signals:**
  
  • [Company/sector: context + thesis]

  **Ecosystem & Future Outlook:**
  
  • [Broader implications or where to learn more]

**Actionable Quotes:**

• "[Memorable quote]"

**Companies/People Mentioned:**

• [Name: context]

**Cross-Episode Themes (if any):**

• [Note if connects to previous episode insight]

---

CRITICAL FORMATTING REQUIREMENTS:
1. ALWAYS put a blank line after section headers before bullet points
2. NEVER put bullet points on the same line as headers
3. Each bullet point must be on its own separate line
4. Use this exact format for ALL sections:

CORRECT FORMAT:
**Section Name:**

• First bullet point here
• Second bullet point here

WRONG FORMAT:
**Section Name:** • First bullet point here
• Second bullet point here

WRONG FORMAT:
**Section Name:**
• First bullet point here • Second bullet point here

Here is the transcript:
{{transcript}}""",
            labels=["production", "podcast", "user"],
            type="text"
        )
        print("✅ Created summarizer user prompt: podcast-summarization-user")

        # 5. Chat Messages Template
        chat_prompt = langfuse.create_prompt(
            name="podcast-chat-template",
            prompt=[
                {
                    "role": "system",
                    "content": "{{system_prompt}}"
                },
                {
                    "role": "user", 
                    "content": "{{user_prompt}}"
                }
            ],
            labels=["production", "podcast", "chat"],
            type="chat"
        )
        print("✅ Created chat template: podcast-chat-template")

        # 6. Quick Summary Prompt (for shorter summaries)
        quick_prompt = langfuse.create_prompt(
            name="podcast-quick-summary",
            prompt="""Create a concise summary of this podcast episode:

**Title:** {{title}}

**Quick Summary (3-5 bullets):**
• [Key takeaway 1]
• [Key takeaway 2] 
• [Key takeaway 3]

**Main Topics:** [List 2-3 core topics]

**Notable Mentions:** [Key people/companies mentioned]

Transcript: {{transcript}}""",
            labels=["production", "podcast", "quick"],
            type="text"
        )
        print("✅ Created quick summary prompt: podcast-quick-summary")

        print(f"\n🎉 Successfully created 6 prompts in Langfuse!")
        print(f"📊 View them at: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/prompts")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create prompts: {e}")
        return False

def test_prompt_retrieval():
    """Test retrieving and compiling prompts"""
    
    try:
        from langfuse import Langfuse
        
        langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000')
        )
        
        print("\n🔍 Testing prompt retrieval...")
        
        # Test retrieving system prompt
        system_prompt = langfuse.get_prompt("podcast-analyzer-system")
        print(f"✅ Retrieved system prompt: {system_prompt.prompt[:50]}...")
        
        # Test retrieving and compiling user prompt
        user_prompt = langfuse.get_prompt("podcast-summarization-user")
        compiled_user = user_prompt.compile(
            title="Test Podcast Episode",
            transcript="This is a test transcript about AI and product management..."
        )
        print(f"✅ Compiled user prompt: {compiled_user[:80]}...")
        
        # Test chat template
        chat_template = langfuse.get_prompt("podcast-chat-template")
        print(f"✅ Retrieved chat template with {len(chat_template.prompt)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test prompts: {e}")
        return False

def main():
    """Setup Langfuse prompts for podcast analysis"""
    print("🎯 Langfuse Prompt Management Setup")
    print("=" * 40)
    
    # Check environment variables
    required_vars = ['LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    # Create prompts
    creation_success = create_podcast_prompts()
    if not creation_success:
        return False
    
    # Test retrieval  
    test_success = test_prompt_retrieval()
    if not test_success:
        return False
    
    print(f"\n🎊 Prompt Management Setup Complete!")
    print(f"📋 Next steps:")
    print(f"1. Visit {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/prompts to see your prompts")
    print(f"2. Try editing a prompt version in the Langfuse UI")
    print(f"3. Run your podcast analyzer to see prompts in action")
    print(f"4. Check the 'Generations' tab to see prompt usage")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)