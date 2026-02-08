"""
Audio transcription using faster-whisper with chunked processing
to avoid OOM on long episodes.
"""
import os
import subprocess
import tempfile
import json
from pathlib import Path
from faster_whisper import WhisperModel
import time
from datetime import datetime

# Maximum chunk duration in seconds (30 minutes).
# Keeps peak memory well under 2 GB even for stereo 44.1 kHz audio.
CHUNK_DURATION_S = 1800

# Files longer than this threshold (in seconds) will be split into chunks.
CHUNK_THRESHOLD_S = 2400  # 40 minutes


class AudioTranscriber:
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.debug = True
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

    def _get_audio_duration(self, audio_file_path):
        """Get duration of audio file in seconds using ffprobe."""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(audio_file_path)],
                capture_output=True, text=True, timeout=30,
            )
            info = json.loads(result.stdout)
            return float(info["format"]["duration"])
        except Exception as e:
            self._debug_log(f"Could not determine duration via ffprobe: {e}")
            return None

    def _split_audio(self, audio_file_path, tmp_dir):
        """Split audio into chunks using ffmpeg. Returns list of chunk paths."""
        chunk_pattern = os.path.join(tmp_dir, "chunk_%03d.mp3")
        cmd = [
            "ffmpeg", "-i", str(audio_file_path),
            "-f", "segment", "-segment_time", str(CHUNK_DURATION_S),
            "-c", "copy",  # no re-encoding, fast
            "-y", chunk_pattern,
        ]
        self._debug_log(f"Splitting audio into {CHUNK_DURATION_S}s chunks...")
        subprocess.run(cmd, capture_output=True, timeout=120, check=True)

        chunks = sorted(Path(tmp_dir).glob("chunk_*.mp3"))
        self._debug_log(f"Created {len(chunks)} chunks")
        return chunks

    def _transcribe_single(self, audio_file_path):
        """Transcribe a single audio file and return (text, segment_count)."""
        segments, info = self.model.transcribe(str(audio_file_path), beam_size=5)
        texts = []
        count = 0
        for seg in segments:
            texts.append(seg.text.strip())
            count += 1
        return " ".join(texts), count

    def transcribe(self, audio_file_path, title="Podcast Episode"):
        """Transcribe audio file using faster-whisper, chunking long files."""
        self._debug_log(f"Starting transcription for: {title}")
        self._debug_log(f"Using model: {self.model_size}")

        start_time = time.time()

        try:
            duration = self._get_audio_duration(audio_file_path)
            if duration:
                self._debug_log(f"Audio duration: {duration:.0f}s ({duration/60:.1f}m)")

            needs_chunking = duration is not None and duration > CHUNK_THRESHOLD_S

            if needs_chunking:
                transcript_text = self._transcribe_chunked(audio_file_path)
            else:
                transcript_text = self._transcribe_whole(audio_file_path)

            if transcript_text is None:
                return None

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

    def _transcribe_whole(self, audio_file_path):
        """Transcribe a single file without chunking (original behaviour)."""
        segments, info = self.model.transcribe(str(audio_file_path), beam_size=5)
        self._debug_log(f"Detected language '{info.language}' with probability {info.language_probability}")

        full_transcript = []
        for i, segment in enumerate(segments):
            full_transcript.append(segment.text.strip())
            if self.debug and (i % 20 == 0 or i == 0):
                self._debug_log(f" > Transcribed segment {i+1}...")

        return " ".join(full_transcript)

    def _transcribe_chunked(self, audio_file_path):
        """Split audio into chunks, transcribe each, and combine."""
        self._debug_log("File is long — using chunked transcription to avoid OOM")

        with tempfile.TemporaryDirectory(prefix="whisper_chunks_") as tmp_dir:
            chunks = self._split_audio(audio_file_path, tmp_dir)
            if not chunks:
                self._debug_log("No chunks produced by ffmpeg split")
                return None

            all_texts = []
            total_segments = 0

            for idx, chunk_path in enumerate(chunks):
                self._debug_log(f"Transcribing chunk {idx+1}/{len(chunks)}: {chunk_path.name}")
                text, seg_count = self._transcribe_single(chunk_path)
                total_segments += seg_count
                all_texts.append(text)
                self._debug_log(f" > Chunk {idx+1} done: {seg_count} segments")

            self._debug_log(f"All chunks transcribed. Total segments: {total_segments}")
            return " ".join(all_texts)