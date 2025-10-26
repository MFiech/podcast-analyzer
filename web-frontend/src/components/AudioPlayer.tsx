'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { PlayCircle, PauseCircle, Volume2 } from 'lucide-react';

interface AudioPlayerProps {
  audioUrl: string;
  title?: string;
}

function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

export function AudioPlayer({ audioUrl, title }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleProgressChange = (value: number[]) => {
    if (audioRef.current) {
      audioRef.current.currentTime = value[0];
      setCurrentTime(value[0]);
    }
  };

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0];
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  return (
    <div className="fixed bottom-16 md:fixed md:bottom-0 left-0 right-0 bg-gradient-to-b from-blue-100 to-blue-50 border-t border-blue-200 p-4 z-40">
      <audio ref={audioRef} src={audioUrl} />
      
      <div className="max-w-4xl mx-auto">
        {title && <p className="text-sm font-semibold text-gray-700 mb-3 truncate">{title}</p>}
        
        <Slider
          value={[currentTime]}
          min={0}
          max={duration || 0}
          step={0.1}
          onValueChange={handleProgressChange}
          className="mb-3"
        />
        
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Button
              onClick={togglePlayPause}
              variant="ghost"
              size="icon"
              className="h-24 w-24"
            >
              {isPlaying ? (
                <PauseCircle className="w-16 h-16 text-blue-600" />
              ) : (
                <PlayCircle className="w-16 h-16 text-blue-600" />
              )}
            </Button>
            <span className="text-xs font-medium w-12 text-right">
              {formatTime(currentTime)}
            </span>
          </div>
          
          <div className="text-xs text-gray-600 flex-shrink-0">
            {formatTime(currentTime)} / {formatTime(duration)}
          </div>
          
          <div className="flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-gray-600" />
            <Slider
              value={[volume]}
              min={0}
              max={1}
              step={0.1}
              onValueChange={handleVolumeChange}
              className="w-16"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
