'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { MoreVertical, Edit2, Trash2 } from 'lucide-react';
import { Feed, FEED_CATEGORIES } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { deleteFeed } from '@/lib/api';
import { toast } from 'sonner';

interface FeedCardProps {
  feed: Feed;
  onEdit: (feed: Feed) => void;
}

const statusConfig = {
  active: { dot: '🟢', label: 'Active' },
  error: { dot: '🔴', label: 'Error' },
};

export function FeedCard({ feed, onEdit }: FeedCardProps) {
  const queryClient = useQueryClient();
  const feedStatus = (feed.status || 'active') as keyof typeof statusConfig;
  const statusInfo = statusConfig[feedStatus];

  const { mutate: handleDelete, isPending } = useMutation({
    mutationFn: () => deleteFeed(feed.id),
    onSuccess: () => {
      toast.success('Feed deleted');
      queryClient.invalidateQueries({ queryKey: ['feeds'] });
    },
    onError: () => toast.error('Failed to delete feed'),
  });

  return (
    <Card className="p-4 mb-3">
      <div className="flex gap-3 items-start">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span>{statusInfo.dot}</span>
            <h3 className="font-semibold text-gray-900 line-clamp-1">{feed.title}</h3>
          </div>
          <p className="text-xs text-gray-500 line-clamp-1 mb-2">{feed.url}</p>
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <span>{feed.episode_count} episodes</span>
            {feed.category && (
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                {FEED_CATEGORIES.find(c => c.value === feed.category)?.label || feed.category}
              </Badge>
            )}
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-10 w-10 flex-shrink-0">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(feed)}>
              <Edit2 className="w-4 h-4 mr-2" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleDelete()} disabled={isPending} className="text-red-600">
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </Card>
  );
}
