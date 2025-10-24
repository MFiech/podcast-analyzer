"""
Transcript cleaning using OpenAI - following Tomasz Tunguz's approach
"""
import time
import os
from datetime import datetime
from langfuse.openai import openai  # Langfuse OpenAI wrapper for automatic tracing
from langfuse import Langfuse, observe

class TranscriptCleaner:
    def __init__(self):
        self.debug = True
        # Langfuse OpenAI wrapper is automatically configured via env vars
        # No manual OpenAI client initialization needed

        # Initialize Langfuse client for prompt management
        self.langfuse_enabled = os.getenv('LANGFUSE_ENABLED', 'true').lower() == 'true'
        if self.langfuse_enabled:
            try:
                self.langfuse = Langfuse()
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
            print(f"[{timestamp}] CLEANER: {message}")
    
    @observe(as_type="generation")
    def clean_transcript(self, raw_transcript, title="Podcast Episode"):
        """Clean up transcript using OpenAI API with Langfuse Prompt Management"""
        self._debug_log(f"Starting transcript cleaning for: {title}")
        self._debug_log(f"Raw transcript length: {len(raw_transcript)} characters, {len(raw_transcript.split())} words")

        # Calculate estimated tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_input_tokens = len(raw_transcript) // 4
        self._debug_log(f"Estimated input tokens: ~{estimated_input_tokens}")

        # Get prompts from Langfuse Prompt Management
        system_prompt_text = ""
        user_prompt_text = ""
        langfuse_prompt = None  # For linking prompt to observation

        try:
            if self.langfuse_enabled and self.langfuse:
                self._debug_log("📋 Fetching prompts from Langfuse Prompt Management...")

                # Get system prompt
                system_prompt_obj = self.langfuse.get_prompt("podcast-transcript-cleaner-system", label="production")
                system_prompt_text = system_prompt_obj.prompt

                # Get and compile user prompt with variables
                user_prompt_obj = self.langfuse.get_prompt("podcast-transcript-cleaner-user", label="production")
                user_prompt_text = user_prompt_obj.compile(raw_transcript=raw_transcript)

                # Store prompt object for automatic linking
                langfuse_prompt = user_prompt_obj

                self._debug_log("✅ Successfully loaded prompts from Langfuse")
            else:
                raise Exception("Langfuse not enabled, using fallback prompts")

        except Exception as e:
            self._debug_log(f"⚠️  Failed to load Langfuse prompts, using fallback: {str(e)}")
            # Fallback to hardcoded prompts
            system_prompt_text = """You are a professional transcript cleaner.
Your task is to remove filler words (um, ah, like, you know, etc.)
and small-talk fluff while preserving all technical, business, and conversational content.
Do not shorten or summarize — keep the transcript length and meaning intact."""

            user_prompt_text = f"""Clean the following podcast transcript while preserving all content.
Keep the same length, remove fillers and irrelevant small-talk,
and make sure technical/business details remain untouched.

Transcript:
{raw_transcript}"""
        
        try:
            self._debug_log("🚀 Sending request to OpenAI API...")
            self._debug_log("📡 Model: gpt-4o-mini (fast & free)")
            self._debug_log("⚙️  Temperature: 0.3 (conservative for cleaning)")
            self._debug_log("📝 Max output tokens: 4000")
            
            start_time = time.time()

            # Prepare messages using the prompt management system
            messages = [
                {"role": "system", "content": system_prompt_text},
                {"role": "user", "content": user_prompt_text}
            ]

            # Use Langfuse OpenAI wrapper (automatic tracing + prompt linking)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=4000,
                langfuse_prompt=langfuse_prompt  # Links prompt to observation
            )

            # Log prompt source for debugging
            prompt_source = "langfuse_prompt_management" if langfuse_prompt else "fallback"
            self._debug_log(f"🔗 Used prompts from: {prompt_source}")
            
            elapsed = time.time() - start_time
            
            # Extract usage information
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            self._debug_log(f"✅ OpenAI cleaning completed in {elapsed:.2f}s")
            self._debug_log(f"📊 Token usage: {input_tokens} input + {output_tokens} output = {total_tokens} total")
            self._debug_log(f"⚡ Processing speed: {total_tokens/elapsed:.1f} tokens/second")
            
            cleaned = response.choices[0].message.content
            self._debug_log(f"📝 Transcript cleaned: {len(raw_transcript.split())} -> {len(cleaned.split())} words")
            self._debug_log(f"📉 Compression ratio: {len(cleaned)/len(raw_transcript)*100:.1f}% of original length")

            return cleaned
            
        except Exception as e:
            self._debug_log(f"❌ Error with OpenAI cleaning: {str(e)}")
            raise RuntimeError(f"Failed to clean transcript with OpenAI: {str(e)}")