'use client';

import React, { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { PlayCircle, StopCircle } from 'lucide-react';

const SPEEDS = [1, 1.25, 1.5, 2] as const;

function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00';
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

interface SummaryPlayerProps {
  summaryText?: string;
}

export function SummaryPlayer({ summaryText }: SummaryPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<(typeof SPEEDS)[number]>(1);

  const duration = useMemo(() => {
    if (!summaryText) return 300;
    const wordCount = summaryText.split(/\s+/).length;
    const minutes = wordCount / 150;
    return Math.max(60, Math.round(minutes * 60));
  }, [summaryText]);

  const togglePlayStop = () => {
    if (isPlaying) {
      setIsPlaying(false);
      setCurrentTime(0);
    } else {
      setIsPlaying(true);
    }
  };

  const cycleSpeed = () => {
    const currentIndex = SPEEDS.indexOf(playbackSpeed);
    const nextIndex = (currentIndex + 1) % SPEEDS.length;
    setPlaybackSpeed(SPEEDS[nextIndex]);
  };

  const handleTimeChange = (value: number[]) => {
    setCurrentTime(value[0]);
  };

  const playerContent = (
    <div className="bg-gradient-to-b from-blue-100 to-blue-50 p-4">
      <div className="flex items-center gap-3 max-w-4xl mx-auto">
        <Button variant="ghost" size="icon" onClick={togglePlayStop} className="h-10 w-10 flex-shrink-0">
          {isPlaying ? (
            <StopCircle className="w-16 h-16 text-blue-600" />
          ) : (
            <PlayCircle className="w-16 h-16 text-blue-600" />
          )}
        </Button>

        <span className="text-xs font-medium text-gray-600 w-10 text-right tabular-nums">
          {formatTime(currentTime)}
        </span>

        <Slider
          value={[currentTime]}
          min={0}
          max={duration}
          step={1}
          onValueChange={handleTimeChange}
          className="flex-1"
        />

        <span className="text-xs font-medium text-gray-600 w-10 tabular-nums">
          {formatTime(duration)}
        </span>

        <Button
          variant="ghost"
          size="sm"
          onClick={cycleSpeed}
          className="text-xs font-bold text-blue-600 w-[3.5rem] px-2"
        >
          {playbackSpeed}x
        </Button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop: inline card above AI Summary */}
      <div className="hidden md:block mb-6 rounded-lg border border-blue-200 overflow-hidden">
        {playerContent}
      </div>

      {/* Mobile: fixed bar above bottom nav */}
      <div className="fixed bottom-16 left-0 right-0 md:hidden z-[35] border-t border-blue-200">
        {playerContent}
      </div>
    </>
  );
}
