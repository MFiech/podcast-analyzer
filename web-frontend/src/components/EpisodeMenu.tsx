'use client';

import React from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { MoreVertical, RotateCcw, RefreshCw, Eraser, Trash2 } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { summarizeAgain, retryEpisode, recleanEpisode, deleteEpisode } from '@/lib/api';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

interface EpisodeMenuProps {
  episodeId: string;
  hasTranscript?: boolean;
  status?: string;
}

export function EpisodeMenu({ episodeId, hasTranscript = true, status }: EpisodeMenuProps) {
  const queryClient = useQueryClient();
  const router = useRouter();

  const { mutate: handleSummarizeAgain, isPending: isSummarizePending } = useMutation({
    mutationFn: () => summarizeAgain(episodeId),
    onSuccess: () => {
      toast.success('Episode queued for re-summarization');
      queryClient.invalidateQueries({ queryKey: ['episode', episodeId] });
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.error || 'Failed to queue episode for re-summarization';
      toast.error(errorMessage);
    },
  });

  const { mutate: handleReclean, isPending: isRecleanPending } = useMutation({
    mutationFn: () => recleanEpisode(episodeId),
    onSuccess: () => {
      toast.success('Episode queued for re-cleaning');
      queryClient.invalidateQueries({ queryKey: ['episode', episodeId] });
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.error || 'Failed to re-clean episode';
      toast.error(errorMessage);
    },
  });

  const { mutate: handleRetry, isPending: isRetryPending } = useMutation({
    mutationFn: () => retryEpisode(episodeId),
    onSuccess: () => {
      toast.success('Episode queued for retry');
      queryClient.invalidateQueries({ queryKey: ['episode', episodeId] });
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.error || 'Failed to retry episode';
      toast.error(errorMessage);
    },
  });

  const { mutate: handleDelete, isPending: isDeletePending } = useMutation({
    mutationFn: () => deleteEpisode(episodeId),
    onSuccess: () => {
      toast.success('Episode deleted');
      router.push('/');
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.error || 'Failed to delete episode';
      toast.error(errorMessage);
    },
  });

  const showRetry = status === 'processing' || status === 'failed';
  const showCompletedActions = status === 'completed' && hasTranscript;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-10 w-10">
          <MoreVertical className="w-5 h-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {showRetry && (
          <>
            <DropdownMenuItem
              onClick={() => handleRetry()}
              disabled={isRetryPending}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              {isRetryPending ? 'Retrying...' : 'Retry'}
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => handleDelete()}
              disabled={isDeletePending}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              {isDeletePending ? 'Deleting...' : 'Delete'}
            </DropdownMenuItem>
          </>
        )}
        {showCompletedActions && (
          <>
            <DropdownMenuItem
              onClick={() => handleReclean()}
              disabled={isRecleanPending}
            >
              <Eraser className="w-4 h-4 mr-2" />
              {isRecleanPending ? 'Re-cleaning...' : 'Re-clean'}
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => handleSummarizeAgain()}
              disabled={isSummarizePending}
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              {isSummarizePending ? 'Queuing...' : 'Re-summarize'}
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => handleDelete()}
              disabled={isDeletePending}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              {isDeletePending ? 'Deleting...' : 'Delete'}
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
