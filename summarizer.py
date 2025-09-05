"""
Podcast summarization using OpenAI
"""
import time
import os
from datetime import datetime
from openai import OpenAI
from langfuse import Langfuse, observe

class PodcastSummarizer:
    def __init__(self):
        self.debug = True
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not self.openai_client.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize Langfuse for tracing (if enabled)
        self.langfuse_enabled = os.getenv('LANGFUSE_ENABLED', 'true').lower() == 'true'
        if self.langfuse_enabled:
            try:
                self.langfuse = Langfuse(
                    secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
                    public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
                    host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000'),
                    flush_at=1,  # Flush after 1 event instead of batching
                    flush_interval=1  # Flush every 1 second
                )
            except Exception as e:
                self._debug_log(f"⚠️  Warning: Failed to initialize Langfuse: {str(e)}")
                self.langfuse_enabled = False
                self.langfuse = None
        else:
            self.langfuse = None
        
    def _debug_log(self, message):
        """Debug logging with timestamp"""
        if self.debug:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] SUMMARIZER: {message}")
    
    @observe(as_type="generation", name="podcast_summarization")
    def summarize(self, transcript, title="Podcast Episode"):
        """Generate summary from transcript using OpenAI API with Langfuse Prompt Management"""
        self._debug_log(f"Starting summarization for: {title}")
        self._debug_log(f"Transcript length: {len(transcript)} characters, {len(transcript.split())} words")
        
        # Calculate estimated tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_input_tokens = len(transcript) // 4
        self._debug_log(f"Estimated input tokens: ~{estimated_input_tokens}")
        
        # Get prompts from Langfuse Prompt Management
        system_prompt_text = ""
        user_prompt_text = ""
        
        try:
            if self.langfuse_enabled and self.langfuse:
                self._debug_log("📋 Fetching prompts from Langfuse Prompt Management...")
                
                # Get system prompt
                system_prompt = self.langfuse.get_prompt("podcast-analyzer-system", label="production")
                system_prompt_text = system_prompt.prompt
                
                # Get and compile user prompt with variables
                user_prompt = self.langfuse.get_prompt("podcast-summarization-user", label="production")
                user_prompt_text = user_prompt.compile(
                    title=title,
                    transcript=transcript
                )
                
                self._debug_log("✅ Successfully loaded prompts from Langfuse")
            else:
                raise Exception("Langfuse not enabled, using fallback prompts")
                
        except Exception as e:
            self._debug_log(f"⚠️  Failed to load Langfuse prompts, using fallback: {str(e)}")
            # Fallback to hardcoded prompts
            system_prompt_text = """You are a professional podcast analyst. 
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
            
            user_prompt_text = f"""
Please analyze this podcast transcript and produce a structured summary with two layers:

---

**TL;DR (quick read):**

• 3–5 bullets summarizing the main takeaways (~100 words max)

---

**Detailed Notes:**

**Title:** {title}

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
{transcript}
Here is the transcript:
{transcript}
        """
        
        try:
            self._debug_log("🚀 Sending request to OpenAI API...")
            self._debug_log("📡 Model: gpt-4o-mini (fast & free)")
            self._debug_log("⚙️  Temperature: 0.7 (balanced creativity)")
            self._debug_log("📝 Max output tokens: 2000")
            
            start_time = time.time()
            
            # Prepare messages using the prompt management system
            messages = [
                {"role": "system", "content": system_prompt_text},
                {"role": "user", "content": user_prompt_text}
            ]
            
            # Use OpenAI API with managed prompts
            # The @observe decorator will automatically track this as a generation
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and free
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Log prompt source for debugging
            prompt_source = "langfuse_prompt_management" if "podcast analyst" in system_prompt_text else "fallback"
            self._debug_log(f"🔗 Used prompts from: {prompt_source}")
            
            elapsed = time.time() - start_time
            
            # Extract usage information
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            self._debug_log(f"✅ OpenAI summarization completed in {elapsed:.2f}s")
            self._debug_log(f"📊 Token usage: {input_tokens} input + {output_tokens} output = {total_tokens} total")
            self._debug_log(f"⚡ Processing speed: {total_tokens/elapsed:.1f} tokens/second")
            
            summary = response.choices[0].message.content
            self._debug_log(f"📝 Summary generated: {len(summary)} characters")
            self._debug_log(f"📉 Summary ratio: {len(summary)/len(transcript)*100:.1f}% of transcript length")
            
            # Flush traces to Langfuse (with error handling)
            if self.langfuse_enabled and self.langfuse:
                try:
                    self.langfuse.flush()
                except Exception as e:
                    self._debug_log(f"⚠️  Warning: Failed to flush traces to Langfuse: {str(e)}")
                    # Don't fail the entire operation if tracing fails
            
            return summary
            
        except Exception as e:
            self._debug_log(f"❌ Error with OpenAI summarization: {str(e)}")
            raise RuntimeError(f"Failed to generate summary with OpenAI: {str(e)}")
    
