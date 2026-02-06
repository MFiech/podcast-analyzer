#!/usr/bin/env python3
"""
Script to create and manage prompts in Langfuse for podcast summarization.
Creates category-specific summarization prompts and a shared transcript cleaner prompt.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Category definitions: (category_key, display_name, langfuse_prompt_name)
PODCAST_CATEGORIES = [
    ("general", "General", "podcast-summarization"),
    ("news", "News", "podcast-summarization-news"),
    ("products_ai", "Products & AI", "podcast-summarization-products-ai"),
    ("spanish_learning", "Spanish Learning", "podcast-summarization-spanish-learning"),
]


def _build_system_message(category_display_name):
    """Build the system message for a category-specific summarization prompt."""
    return f"""[{category_display_name}] You are a professional podcast analyst.
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
- Companies/people should always be noted with context."""


USER_MESSAGE_TEMPLATE = """Please analyze this podcast transcript and produce a structured summary with two layers:

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
{{transcript}}"""


def create_podcast_prompts():
    """Create chat prompts for podcast analysis in Langfuse (best practice: combine system + user)"""

    try:
        from langfuse import Langfuse

        langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000')
        )

        print("🚀 Creating Langfuse chat prompts for podcast analysis...")
        print("📋 Using best practice: combining system + user messages into chat prompts")

        # 1. Transcript Cleaner Chat Prompt (shared across all categories)
        langfuse.create_prompt(
            name="podcast-transcript-cleaner",
            prompt=[
                {
                    "role": "system",
                    "content": """You are a professional transcript cleaner.
Your task is to remove filler words (um, ah, like, you know, etc.)
and small-talk fluff while preserving all technical, business, and conversational content.
Do not shorten or summarize — keep the transcript length and meaning intact."""
                },
                {
                    "role": "user",
                    "content": """Clean the following podcast transcript while preserving all content.
Keep the same length, remove fillers and irrelevant small-talk,
and make sure technical/business details remain untouched.

Transcript:
{{raw_transcript}}"""
                }
            ],
            labels=["production", "podcast", "cleaner"],
            type="chat",
            config={
                "model": "gpt-4o-mini",
                "temperature": 0.3,
                "max_tokens": 4000
            }
        )
        print("✅ Created cleaner chat prompt: podcast-transcript-cleaner")

        # 2. Category-specific Summarization Chat Prompts
        for category_key, display_name, prompt_name in PODCAST_CATEGORIES:
            langfuse.create_prompt(
                name=prompt_name,
                prompt=[
                    {
                        "role": "system",
                        "content": _build_system_message(display_name)
                    },
                    {
                        "role": "user",
                        "content": USER_MESSAGE_TEMPLATE
                    }
                ],
                labels=["production", "podcast", "summarization", category_key],
                type="chat",
                config={
                    "model": "gpt-4o-mini",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            print(f"✅ Created summarization chat prompt: {prompt_name} [{display_name}]")

        prompt_count = 1 + len(PODCAST_CATEGORIES)  # cleaner + category prompts
        print(f"\n🎉 Successfully created {prompt_count} chat prompts in Langfuse!")
        print(f"📊 View them at: {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/prompts")
        print(f"\n💡 Category prompts created:")
        for category_key, display_name, prompt_name in PODCAST_CATEGORIES:
            print(f"   • {prompt_name} → [{display_name}]")

        return True

    except Exception as e:
        print(f"❌ Failed to create prompts: {e}")
        return False

def test_prompt_retrieval():
    """Test retrieving and compiling chat prompts"""

    try:
        from langfuse import Langfuse

        langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000')
        )

        print("\n🔍 Testing chat prompt retrieval and compilation...")

        # Test 1: Retrieve and compile cleaner chat prompt
        cleaner_prompt = langfuse.get_prompt("podcast-transcript-cleaner", type="chat")
        compiled_cleaner = cleaner_prompt.compile(
            raw_transcript="Um, so like, this is a test transcript, you know, about AI..."
        )
        print(f"✅ Retrieved cleaner chat prompt with {len(cleaner_prompt.prompt)} messages")
        print(f"   Compiled to {len(compiled_cleaner)} messages for OpenAI API")

        # Test 2: Retrieve and compile each category summarization prompt
        for category_key, display_name, prompt_name in PODCAST_CATEGORIES:
            summarizer_prompt = langfuse.get_prompt(prompt_name, label="production", type="chat")
            compiled_summarizer = summarizer_prompt.compile(
                title="Test Podcast Episode",
                transcript="This is a test transcript about AI and product management..."
            )
            print(f"✅ Retrieved [{display_name}] prompt: {len(summarizer_prompt.prompt)} messages → {len(compiled_summarizer)} compiled")

        # Test 3: Verify config is included
        if hasattr(cleaner_prompt, 'config'):
            print(f"✅ Cleaner prompt includes config: {cleaner_prompt.config}")

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
    print(f"1. Visit {os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/prompts to see your chat prompts")
    print(f"2. Try editing a prompt version in the Langfuse UI")
    print(f"3. Run your podcast analyzer to see prompts in action")
    print(f"4. Check prompt observation counts - should now show linked generations")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
