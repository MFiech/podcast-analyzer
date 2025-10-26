'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getFeeds } from '@/lib/api';
import { FeedCard } from '@/components/FeedCard';
import { FeedModal } from '@/components/FeedModal';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Info, Plus } from 'lucide-react';
import { Feed } from '@/lib/api';

export default function FeedsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFeed, setSelectedFeed] = useState<Feed | undefined>();

  const { data: feeds, isLoading, error } = useQuery({
    queryKey: ['feeds'],
    queryFn: getFeeds,
  });

  const handleEdit = (feed: Feed) => {
    setSelectedFeed(feed);
    setIsModalOpen(true);
  };

  const handleAddNew = () => {
    setSelectedFeed(undefined);
    setIsModalOpen(true);
  };

  return (
    <div className="pb-20 md:pb-0">
      <div className="px-4 py-4 max-w-2xl mx-auto">
        <div className="hidden md:block mb-6">
          <h1 className="text-3xl font-bold text-gray-900">RSS Feeds</h1>
          <p className="text-gray-600 mt-1">Manage your podcast RSS feeds</p>
        </div>

        <div className="flex items-center justify-between mb-4 md:mb-6">
          <div>
            <h2 className="text-lg font-semibold">RSS Feeds</h2>
            <p className="text-sm text-gray-600">{feeds?.length || 0} active feeds</p>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-20 rounded-lg" />
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-600">Error loading feeds. Please try again.</p>
          </div>
        ) : feeds && feeds.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">No RSS feeds yet</p>
            <p className="text-sm text-gray-400 mb-6">Add your first feed to get started</p>
            <Button onClick={handleAddNew}>
              <Plus className="w-4 h-4 mr-2" />
              Add RSS Feed
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-0 mb-6">
              {feeds?.map((feed: any) => (
                <FeedCard key={feed.id} feed={feed} onEdit={handleEdit} />
              ))}
            </div>

            <Alert className="bg-blue-50 border-blue-200">
              <Info className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-sm">
                <strong>Adding RSS Feeds:</strong> Most podcast platforms provide RSS URLs in their show settings.
              </AlertDescription>
            </Alert>
          </>
        )}
      </div>

      <div className="fixed bottom-20 md:bottom-0 md:static right-4 md:right-0 md:mt-6 px-4">
        <Button onClick={handleAddNew} size="lg" className="rounded-full md:rounded-lg w-14 h-14 md:w-auto md:h-auto">
          <Plus className="w-6 h-6 md:w-4 md:h-4" />
          <span className="hidden md:inline md:ml-2">Add Feed</span>
        </Button>
      </div>

      <FeedModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} feed={selectedFeed} />
    </div>
  );
}
