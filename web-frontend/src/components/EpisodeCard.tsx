'use client';

import React from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { MoreVertical, RotateCcw, Eye, AlertCircle } from 'lucide-react';
import { Episode } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { hideEpisode, retryEpisode } from '@/lib/api';
import { toast } from 'sonner';

interface EpisodeCardProps {
  episode: Episode;
}

const statusConfig = {
  completed: { label: 'Completed', color: 'bg-green-100 text-green-800' },
  processing: { label: 'Processing', color: 'bg-orange-100 text-orange-800' },
  failed: { label: 'Failed', color: 'bg-red-100 text-red-800' },
};

export function EpisodeCard({ episode }: EpisodeCardProps) {
  const queryClient = useQueryClient();
  const statusInfo = statusConfig[episode.status as keyof typeof statusConfig];

  const { mutate: handleHide } = useMutation({
    mutationFn: () => hideEpisode(episode.id),
    onSuccess: () => {
      toast.success('Episode hidden');
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
    },
    onError: () => toast.error('Failed to hide episode'),
  });

  const { mutate: handleRetry } = useMutation({
    mutationFn: () => retryEpisode(episode.id),
    onSuccess: () => {
      toast.success('Episode queued for retry');
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
    },
    onError: () => toast.error('Failed to retry episode'),
  });
  
  // Helper functions to format data
  const formatDuration = (seconds: number | string) => {
    if (typeof seconds === 'string') return seconds;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${String(secs).padStart(2, '0')}`;
  };
  
  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return 'Unknown';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  return (
    <Card className="p-4 mb-3 hover:shadow-md transition-shadow relative">
      <div className="flex gap-3">
        <Link href={`/episode/${episode.id}`} className="flex-1 min-w-0 cursor-pointer">
          <div>
            <h3 className="font-semibold text-gray-900 line-clamp-2">{episode.title}</h3>
            <p className="text-xs text-gray-600 mt-2">
              📡 {episode.feed_title || episode.feed_source || 'Unknown'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {formatDate(episode.created_at || episode.submitted_date)}
            </p>
            {episode.status === 'processing' && (
              <p className="text-xs text-orange-600 mt-2 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                Processing... Estimated completion: 5 minutes
              </p>
            )}
            {episode.status === 'failed' && (
              <p className="text-xs text-red-600 mt-2 line-clamp-1">
                {episode.summary || 'Processing failed due to audio quality issues'}
              </p>
            )}
          </div>
        </Link>
        <div className="flex flex-col items-end justify-between gap-2">
          <Badge variant="secondary" className={statusInfo.color}>
            {statusInfo.label}
          </Badge>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" onClick={(e) => e.preventDefault()} className="h-8 w-8">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={(e) => {
                e.preventDefault();
                handleHide();
              }}>
                <Eye className="w-4 h-4 mr-2" />
                Hide
              </DropdownMenuItem>
              {episode.status === 'failed' && (
                <DropdownMenuItem onClick={(e) => {
                  e.preventDefault();
                  handleRetry();
                }}>
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Retry
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </Card>
  );
}
