'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getEpisodes, FEED_CATEGORIES } from '@/lib/api';
import { LastSyncBox } from '@/components/LastSyncBox';
import { EpisodeCard } from '@/components/EpisodeCard';
import { AddEpisodeModal } from '@/components/AddEpisodeModal';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus } from 'lucide-react';

const categoryFilters = [
  { value: '', label: 'All' },
  ...FEED_CATEGORIES.filter((c) => c.value !== '_none'),
];

export default function Home() {
  const [limit, setLimit] = useState(10);
  const [category, setCategory] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);

  const { data: episodes, isLoading, error } = useQuery({
    queryKey: ['episodes', limit, category],
    queryFn: () => getEpisodes({ limit, ...(category ? { category } : {}) }),
  });

  const episodesList = episodes?.episodes || [];

  return (
    <div className="px-4 py-4 max-w-4xl mx-auto pb-24 md:pb-4">
      <div className="md:hidden mb-4 flex items-center justify-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
          P
        </div>
        <span className="font-bold text-lg">Podcast Summarizer</span>
      </div>
      <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-6">Episodes</h1>
      <div className="hidden md:block mb-2">
        <p className="text-gray-600 mt-1">Manage and track your podcast episodes</p>
      </div>

      <LastSyncBox />

      {/* Category Filter Chips */}
      <div className="flex gap-2 overflow-x-auto pb-1 mb-4 -mx-1 px-1 scrollbar-hide">
        {categoryFilters.map((filter) => (
          <button
            key={filter.value}
            onClick={() => {
              setCategory(filter.value);
              setLimit(10);
            }}
            className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              category === filter.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-8">
          <p className="text-red-600">Error loading episodes. Please try again.</p>
        </div>
      ) : episodesList.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No episodes found</p>
          <p className="text-sm text-gray-400">Add RSS feeds or manually submit episodes to get started</p>
        </div>
      ) : (
        <>
          <div className="space-y-0">
            {episodesList.map((episode: any) => (
              <EpisodeCard key={episode.id} episode={episode} />
            ))}
          </div>
          {limit < (episodes?.total || 0) && (
            <Button
              onClick={() => setLimit(limit + 10)}
              variant="outline"
              className="w-full mt-4"
            >
              Load More Episodes
            </Button>
          )}
        </>
      )}

      {/* Floating Action Button */}
      <div className="fixed bottom-20 right-4 md:bottom-4">
        <Button
          size="lg"
          onClick={() => setShowAddModal(true)}
          className="rounded-full w-14 h-14 shadow-lg bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-6 h-6" />
        </Button>
      </div>

      <AddEpisodeModal open={showAddModal} onOpenChange={setShowAddModal} />
    </div>
  );
}
