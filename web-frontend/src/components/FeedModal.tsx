'use client';

import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { addFeed, updateFeed, Feed, FeedCategory, FEED_CATEGORIES } from '@/lib/api';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Drawer, DrawerClose, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from '@/components/ui/drawer';
import { useMediaQuery } from '@/lib/hooks/useMediaQuery';

interface FeedModalProps {
  isOpen: boolean;
  onClose: () => void;
  feed?: Feed;
}

export function FeedModal({ isOpen, onClose, feed }: FeedModalProps) {
  console.log('FeedModal rendered with feed:', feed);
  const isDesktop = useMediaQuery('(min-width: 768px)');
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    feed_url: '',
    feed_title: '',
    custom_prompt: '',
    category: '_none',
  });

  useEffect(() => {
    if (isOpen) {
      if (feed) {
        console.log('FeedModal - feed object:', feed);
        console.log('FeedModal - customPromptInstructions:', feed.customPromptInstructions);
        setFormData({
          feed_url: feed.url,
          feed_title: feed.title,
          custom_prompt: feed.customPromptInstructions || '',
          category: feed.category || '_none',
        });
      } else {
        setFormData({ feed_url: '', feed_title: '', custom_prompt: '', category: '_none' });
      }
    }
  }, [isOpen]);

  const { mutate: handleSubmit, isPending } = useMutation({
    mutationFn: async () => {
      if (!formData.feed_url.trim()) {
        throw new Error('Feed URL is required');
      }
      // Convert _none sentinel back to empty string for API
      const category = (formData.category === '_none' ? '' : formData.category) as FeedCategory;
      const payload = {
        ...formData,
        category,
      };
      if (feed) {
        return updateFeed(feed.id, payload);
      } else {
        return addFeed(payload);
      }
    },
    onSuccess: () => {
      toast.success(feed ? 'Feed updated' : 'Feed added');
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.message || (feed ? 'Failed to update feed' : 'Failed to add feed'));
    },
  });

  const content = (
    <div className="space-y-4 py-4">
      <div>
        <Label htmlFor="url">Feed URL *</Label>
        <Input
          id="url"
          placeholder="https://example.com/podcast/feed.xml"
          value={formData.feed_url}
          onChange={(e) => setFormData({ ...formData, feed_url: e.target.value })}
        />
      </div>
      <div>
        <Label htmlFor="title">Feed Title (Optional)</Label>
        <Input
          id="title"
          placeholder="My Podcast"
          value={formData.feed_title}
          onChange={(e) => setFormData({ ...formData, feed_title: e.target.value })}
        />
      </div>
      <div>
        <Label htmlFor="category">Category</Label>
        <Select
          value={formData.category}
          onValueChange={(value) => setFormData({ ...formData, category: value })}
        >
          <SelectTrigger id="category">
            <SelectValue placeholder="General (no category)" />
          </SelectTrigger>
          <SelectContent>
            {FEED_CATEGORIES.map((cat) => (
              <SelectItem key={cat.value} value={cat.value}>
                {cat.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="prompt">Custom Prompt Instructions (Optional)</Label>
        <Textarea
          id="prompt"
          placeholder="Special instructions for AI summarization..."
          value={formData.custom_prompt}
          onChange={(e) => setFormData({ ...formData, custom_prompt: e.target.value })}
          className="min-h-24"
        />
      </div>
      <div className="flex gap-2 justify-end pt-4">
        <Button variant="outline" onClick={onClose} disabled={isPending}>
          Cancel
        </Button>
        <Button onClick={() => handleSubmit()} disabled={isPending}>
          {isPending ? 'Saving...' : feed ? 'Update Feed' : 'Add Feed'}
        </Button>
      </div>
    </div>
  );

  if (isDesktop) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{feed ? 'Edit Feed' : 'Add New Feed'}</DialogTitle>
            <DialogDescription>
              {feed ? 'Update the RSS feed details' : 'Add a new podcast RSS feed'}
            </DialogDescription>
          </DialogHeader>
          {content}
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={isOpen} onOpenChange={onClose}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>{feed ? 'Edit Feed' : 'Add New Feed'}</DrawerTitle>
          <DrawerDescription>
            {feed ? 'Update the RSS feed details' : 'Add a new podcast RSS feed'}
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 pb-4">{content}</div>
      </DrawerContent>
    </Drawer>
  );
}
