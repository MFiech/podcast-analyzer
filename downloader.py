"""
Podcast downloader using yt-dlp
"""
import yt_dlp
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

class PodcastDownloader:
    def __init__(self, audio_dir):
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(exist_ok=True)
        self.debug = True
        
    def _debug_log(self, message):
        """Debug logging with timestamp"""
        if self.debug:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] DOWNLOADER: {message}")
    
    def _get_duration_from_file(self, file_path):
        """Extract duration from audio file using ffprobe"""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1:nokey=1', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(float(result.stdout.strip()))
        except Exception as e:
            self._debug_log(f"ffprobe error: {e}")
        return 0
    
    def download(self, url):
        """Download podcast audio from URL"""
        self._debug_log(f"Starting download from: {url}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.audio_dir / '%(title)s.%(ext)s'),
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': '192K',
            # Add options to bypass bot detection
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info first to get metadata
                self._debug_log("Extracting video metadata...")
                start_time = time.time()
                info = ydl.extract_info(url, download=False)
                elapsed = time.time() - start_time
                
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                self._debug_log(f"Metadata extraction took {elapsed:.2f}s")
                self._debug_log(f"Title: {title}")
                self._debug_log(f"Duration: {duration//60}:{duration%60:02d}")
                
                # Now download
                self._debug_log("Starting audio download...")
                download_start = time.time()
                ydl.download([url])
                download_elapsed = time.time() - download_start
                self._debug_log(f"Download completed in {download_elapsed:.2f}s")
                
                # Find the downloaded file
                self._debug_log("Locating downloaded file...")
                safe_title = title.replace(':', '：')  # YT-DLP may replace colons
                downloaded_files = list(self.audio_dir.glob(f"*{safe_title}*"))
                
                if not downloaded_files:
                    self._debug_log("File not found with exact title, searching for most recent file...")
                    # Try finding the most recently created file
                    all_files = list(self.audio_dir.iterdir())
                    if all_files:
                        downloaded_files = [max(all_files, key=lambda x: x.stat().st_mtime)]
                
                if downloaded_files:
                    file_path = downloaded_files[0]
                    file_size = file_path.stat().st_size / (1024 * 1024)  # Size in MB
                    self._debug_log(f"Found downloaded file: {file_path}")
                    self._debug_log(f"File size: {file_size:.2f} MB")
                    
                    final_duration = duration if duration > 0 else self._get_duration_from_file(str(file_path))
                    self._debug_log(f"Final duration: {final_duration//60}:{final_duration%60:02d}")
                    return {
                        'title': title,
                        'duration': final_duration,
                        'file_path': f'audio/{file_path.name}',
                        'url': url
                    }
                
                self._debug_log("No downloaded file found")
                return None
                
            except Exception as e:
                self._debug_log(f"Error downloading {url}: {str(e)}")
                return None