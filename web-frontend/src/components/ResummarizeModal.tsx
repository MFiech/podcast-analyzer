'use client';

import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { summarizeAgain, EPISODE_CATEGORIES } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from '@/components/ui/drawer';
import { useMediaQuery } from '@/lib/hooks/useMediaQuery';

interface ResummarizeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  episodeId: string;
  currentCategory: string;
}

export function ResummarizeModal({ open, onOpenChange, episodeId, currentCategory }: ResummarizeModalProps) {
  const isDesktop = useMediaQuery('(min-width: 768px)');
  const queryClient = useQueryClient();
  const [selectedCategory, setSelectedCategory] = useState(currentCategory || '_none');

  useEffect(() => {
    if (open) {
      setSelectedCategory(currentCategory || '_none');
    }
  }, [open, currentCategory]);

  const { mutate: handleResummarize, isPending } = useMutation({
    mutationFn: () => summarizeAgain(episodeId, selectedCategory),
    onSuccess: () => {
      toast.success('Episode queued for re-summarization');
      onOpenChange(false);
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
      queryClient.invalidateQueries({ queryKey: ['episode', episodeId] });
    },
    onError: () => toast.error('Failed to queue re-summarization'),
  });

  const content = (
    <div className="space-y-4 py-4">
      <div>
        <Label htmlFor="prompt-category">Prompt Category</Label>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger id="prompt-category">
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            {EPISODE_CATEGORIES.map((cat) => (
              <SelectItem key={cat.value} value={cat.value}>
                {cat.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex gap-2 justify-end pt-4">
        <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isPending}>
          Cancel
        </Button>
        <Button onClick={() => handleResummarize()} disabled={isPending}>
          {isPending ? 'Queuing...' : 'Re-summarize'}
        </Button>
      </div>
    </div>
  );

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Re-summarize Episode</DialogTitle>
            <DialogDescription>
              Choose a prompt category for re-summarization
            </DialogDescription>
          </DialogHeader>
          {content}
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Re-summarize Episode</DrawerTitle>
          <DrawerDescription>
            Choose a prompt category for re-summarization
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 pb-4">{content}</div>
      </DrawerContent>
    </Drawer>
  );
}
