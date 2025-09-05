"""
Transcript cleaning using OpenAI - following Tomasz Tunguz's approach
"""
import time
import os
from datetime import datetime
from openai import OpenAI
from langfuse import Langfuse, observe

class TranscriptCleaner:
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
            print(f"[{timestamp}] CLEANER: {message}")
    
    @observe(as_type="generation")
    def clean_transcript(self, raw_transcript, title="Podcast Episode"):
        """Clean up transcript using OpenAI API"""
        self._debug_log(f"Starting transcript cleaning for: {title}")
        self._debug_log(f"Raw transcript length: {len(raw_transcript)} characters, {len(raw_transcript.split())} words")
        
        # Calculate estimated tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_input_tokens = len(raw_transcript) // 4
        self._debug_log(f"Estimated input tokens: ~{estimated_input_tokens}")
        
        prompt = f"""Clean the following podcast transcript while preserving all content. 
Keep the same length, remove fillers and irrelevant small-talk, 
and make sure technical/business details remain untouched. 

Transcript:
{raw_transcript}
        """
        
        try:
            self._debug_log("🚀 Sending request to OpenAI API...")
            self._debug_log("📡 Model: gpt-4o-mini (fast & free)")
            self._debug_log("⚙️  Temperature: 0.3 (conservative for cleaning)")
            self._debug_log("📝 Max output tokens: 4000")
            
            start_time = time.time()
            
            # Use OpenAI directly (Langfuse will trace via the @observe decorator)
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and free
                messages=[
                    {"role": "system", "content": "You are a professional transcript cleaner. \nYour task is to remove filler words (um, ah, like, you know, etc.) \nand small-talk fluff while preserving all technical, business, and conversational content. \nDo not shorten or summarize — keep the transcript length and meaning intact."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
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
            
            # Flush traces to Langfuse (with error handling)
            if self.langfuse_enabled and self.langfuse:
                try:
                    self.langfuse.flush()
                except Exception as e:
                    self._debug_log(f"⚠️  Warning: Failed to flush traces to Langfuse: {str(e)}")
                    # Don't fail the entire operation if tracing fails
            
            return cleaned
            
        except Exception as e:
            self._debug_log(f"❌ Error with OpenAI cleaning: {str(e)}")
            raise RuntimeError(f"Failed to clean transcript with OpenAI: {str(e)}")