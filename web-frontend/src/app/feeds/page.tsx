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
      <div className="px-4 py-4 max-w-4xl mx-auto">
        <div className="hidden md:block mb-6">
          <h1 className="text-3xl font-bold text-gray-900">RSS Feeds</h1>
          <p className="text-gray-600 mt-1">Manage your podcast RSS feeds</p>
        </div>

        <Alert className="mb-6 bg-blue-50 border-blue-200">
          <Info className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-sm">
            Need help finding RSS feeds? Use <a href="https://getrssfeed.com/" target="_blank" rel="noopener noreferrer" className="font-semibold text-blue-600 hover:underline">getrssfeed.com</a> to find podcast RSS URLs.
          </AlertDescription>
        </Alert>

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
            <p className="text-sm text-gray-400">Tap the + button to add your first feed</p>
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

      {/* Floating Action Button */}
      <div className="fixed bottom-20 right-4 md:bottom-4">
        <Button
          size="lg"
          onClick={handleAddNew}
          className="rounded-full w-14 h-14 shadow-lg bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-6 h-6" />
        </Button>
      </div>

      <FeedModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} feed={selectedFeed} />
    </div>
  );
}
