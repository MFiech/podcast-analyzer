'use client';

import React, { useState } from 'react';
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
import { MoreVertical, RotateCcw, RefreshCw, Eraser, Trash2, AlertCircle, Loader2, XCircle } from 'lucide-react';
import { Episode, EPISODE_CATEGORIES } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { retryEpisode, recleanEpisode, deleteEpisode } from '@/lib/api';
import { toast } from 'sonner';
import { ResummarizeModal } from '@/components/ResummarizeModal';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';

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
  const [showResummarizeModal, setShowResummarizeModal] = useState(false);

  const { mutate: handleRetry } = useMutation({
    mutationFn: () => retryEpisode(episode.id),
    onSuccess: () => {
      toast.success('Episode queued for retry');
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
    },
    onError: () => toast.error('Failed to retry episode'),
  });

  const { mutate: handleReclean } = useMutation({
    mutationFn: () => recleanEpisode(episode.id),
    onSuccess: () => {
      toast.success('Episode queued for re-cleaning');
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
    },
    onError: () => toast.error('Failed to re-clean episode'),
  });

  const { mutate: handleDelete } = useMutation({
    mutationFn: () => deleteEpisode(episode.id),
    onSuccess: () => {
      toast.success('Episode deleted');
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
    },
    onError: () => toast.error('Failed to delete episode'),
  });

  // Helper functions to format data
  const formatDuration = (seconds: number | string) => {
    if (typeof seconds === 'string') return seconds;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${String(secs).padStart(2, '0')}`;
  };

  const formatDate = (dateStr: string | any | undefined) => {
    if (!dateStr) return 'Unknown';
    try {
      let date: Date;
      // Handle BSON extended JSON format: {"$date": "..."}
      if (typeof dateStr === 'object' && dateStr.$date) {
        date = new Date(dateStr.$date);
      } else {
        date = new Date(dateStr);
      }
      if (isNaN(date.getTime())) return 'Unknown';

      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());

      if (dateOnly.getTime() === today.getTime()) return 'Today';
      if (dateOnly.getTime() === yesterday.getTime()) return 'Yesterday';

      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return 'Unknown';
    }
  };

  const getCategoryLabel = () => {
    const cat = episode.prompt_category;
    if (!cat || cat === '_none' || cat === '') return 'General';
    const found = EPISODE_CATEGORIES.find((c) => c.value === cat);
    return found ? found.label : 'General';
  };

  return (
    <>
      <Card className="p-4 mb-3 hover:shadow-md transition-shadow relative">
        <div className="flex gap-3">
          <Link href={`/episode/${episode.id}`} className="flex-1 min-w-0 cursor-pointer">
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="font-semibold text-gray-900 line-clamp-2">{episode.title}</h3>
                {episode.status === 'processing' && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="flex-shrink-0">
                        <Loader2 className="w-4 h-4 text-orange-500 animate-spin" />
                      </span>
                    </TooltipTrigger>
                    <TooltipContent>Processing... Estimated completion: 5 minutes</TooltipContent>
                  </Tooltip>
                )}
                {episode.status === 'failed' && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="flex-shrink-0">
                        <XCircle className="w-4 h-4 text-red-500" />
                      </span>
                    </TooltipTrigger>
                    <TooltipContent>
                      {episode.summary || 'Processing failed due to audio quality issues'}
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
              <p className="text-xs text-gray-600 mt-2">
                📡 {episode.feed_title || episode.feed_source || 'Unknown'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {formatDate(episode.created_at || episode.submitted_date)}
              </p>
            </div>
          </Link>
          <div className="flex flex-col items-end justify-between gap-2">
            {episode.status === 'completed' ? (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                {getCategoryLabel()}
              </Badge>
            ) : null}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" onClick={(e) => e.preventDefault()} className="h-8 w-8">
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {(episode.status === 'failed' || episode.status === 'processing') ? (
                  <>
                    <DropdownMenuItem onClick={(e) => {
                      e.preventDefault();
                      handleRetry();
                    }}>
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Retry
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={(e) => {
                      e.preventDefault();
                      handleDelete();
                    }}>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </>
                ) : episode.status === 'completed' ? (
                  <>
                    <DropdownMenuItem onClick={(e) => {
                      e.preventDefault();
                      handleReclean();
                    }}>
                      <Eraser className="w-4 h-4 mr-2" />
                      Re-clean
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={(e) => {
                      e.preventDefault();
                      setShowResummarizeModal(true);
                    }}>
                      <RotateCcw className="w-4 h-4 mr-2" />
                      Re-summarize
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={(e) => {
                      e.preventDefault();
                      handleDelete();
                    }}>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </>
                ) : null}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </Card>
      <ResummarizeModal
        open={showResummarizeModal}
        onOpenChange={setShowResummarizeModal}
        episodeId={episode.id}
        currentCategory={episode.prompt_category || ''}
      />
    </>
  );
}
