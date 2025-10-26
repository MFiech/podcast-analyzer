'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getEpisodes } from '@/lib/api';
import { LastSyncBox } from '@/components/LastSyncBox';
import { EpisodeCard } from '@/components/EpisodeCard';
import { AddEpisodeModal } from '@/components/AddEpisodeModal';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus } from 'lucide-react';

export default function Home() {
  const [limit, setLimit] = useState(10);
  const [showAddModal, setShowAddModal] = useState(false);

  const { data: episodes, isLoading, error } = useQuery({
    queryKey: ['episodes', limit],
    queryFn: () => getEpisodes({ limit }),
  });

  const episodesList = episodes?.episodes || [];

  return (
    <div className="px-4 py-4 max-w-4xl mx-auto pb-24 md:pb-4">
      <div className="md:hidden mb-6 flex items-center justify-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
          P
        </div>
        <span className="font-bold text-lg">Podcast Summarizer</span>
      </div>
      <div className="hidden md:block mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Episodes</h1>
        <p className="text-gray-600 mt-1">Manage and track your podcast episodes</p>
      </div>

      <LastSyncBox />

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
