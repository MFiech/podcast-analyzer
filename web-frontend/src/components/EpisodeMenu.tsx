'use client';

import React from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { MoreVertical, RotateCcw } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { summarizeAgain } from '@/lib/api';
import { toast } from 'sonner';

interface EpisodeMenuProps {
  episodeId: string;
}

export function EpisodeMenu({ episodeId }: EpisodeMenuProps) {
  const queryClient = useQueryClient();
  
  const { mutate: handleSummarizeAgain, isPending } = useMutation({
    mutationFn: () => summarizeAgain(episodeId),
    onSuccess: () => {
      toast.success('Episode queued for re-summarization');
      queryClient.invalidateQueries({ queryKey: ['episode', episodeId] });
    },
    onError: () => toast.error('Failed to queue episode for re-summarization'),
  });

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-10 w-10">
          <MoreVertical className="w-5 h-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleSummarizeAgain()} disabled={isPending}>
          <RotateCcw className="w-4 h-4 mr-2" />
          {isPending ? 'Queuing...' : 'Summarize Again'}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
