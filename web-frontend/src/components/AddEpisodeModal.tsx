'use client';

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { addEpisode } from '@/lib/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

interface AddEpisodeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddEpisodeModal({ open, onOpenChange }: AddEpisodeModalProps) {
  const [url, setUrl] = useState('');
  const queryClient = useQueryClient();

  const { mutate: handleAddEpisode, isPending } = useMutation({
    mutationFn: () => addEpisode(url),
    onSuccess: () => {
      toast.success('Episode queued for analysis');
      setUrl('');
      onOpenChange(false);
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
    },
    onError: () => toast.error('Failed to add episode'),
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Episode</DialogTitle>
          <DialogDescription>
            Paste the URL of a podcast episode to analyze
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <Input
            placeholder="https://example.com/episode.mp3"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={() => handleAddEpisode()}
              disabled={!url || isPending}
              className="flex-1"
            >
              {isPending ? 'Adding...' : 'Add'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}