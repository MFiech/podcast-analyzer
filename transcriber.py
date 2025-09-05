"""
Audio transcription using faster-whisper
"""
import os
from pathlib import Path
from faster_whisper import WhisperModel
import time
from datetime import datetime

class AudioTranscriber:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.debug = True
        # Using GPU with float16 is faster, but CPU with int8 is a good fallback
        # This will automatically use the best available device.
        self.model = WhisperModel(model_size, device="auto", compute_type="int8")
    
    def _debug_log(self, message):
        """Debug logging with timestamp"""
        if self.debug:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] TRANSCRIBER: {message}")

    def get_transcript_path(self, title):
        """Get the path for the transcript file."""
        sanitized_title = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_')).rstrip()
        transcript_filename = f"{sanitized_title.replace(' ', '_')}.txt"
        return Path("data/transcripts") / transcript_filename

    def transcribe(self, audio_file_path, title="Podcast Episode"):
        """Transcribe audio file using faster-whisper"""
        self._debug_log(f"Starting transcription for: {title}")
        self._debug_log(f"Using model: {self.model_size}")
        
        start_time = time.time()
        
        try:
            segments, info = self.model.transcribe(str(audio_file_path), beam_size=5)

            self._debug_log(f"Detected language '{info.language}' with probability {info.language_probability}")
            
            full_transcript = []
            
            for i, segment in enumerate(segments):
                text = segment.text.strip()
                full_transcript.append(text)
                if self.debug and (i % 20 == 0 or i == 0):
                    self._debug_log(f" > Transcribed segment {i+1}...")

            transcript_text = " ".join(full_transcript)
            
            elapsed = time.time() - start_time
            self._debug_log(f"Transcription completed in {elapsed:.2f}s")
            
            # Save transcript to file
            transcript_path = self.get_transcript_path(title)
            transcript_path.parent.mkdir(exist_ok=True)
            transcript_path.write_text(transcript_text, encoding='utf-8')
            self._debug_log(f"Transcript saved to: {transcript_path}")

            return transcript_text
            
        except Exception as e:
            self._debug_log(f"Error during transcription: {str(e)}")
            return None