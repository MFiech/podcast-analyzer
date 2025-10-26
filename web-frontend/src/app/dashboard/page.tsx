'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getEpisodes } from '@/lib/api';
import { LastSyncBox } from '@/components/LastSyncBox';
import { StatsCards } from '@/components/StatsCards';
import { EpisodeCard } from '@/components/EpisodeCard';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardPage() {
  const [filter, setFilter] = useState<'all' | 'completed' | 'processing'>('all');
  const [limit, setLimit] = useState(10);

  const { data: episodes, isLoading, error } = useQuery({
    queryKey: ['episodes', filter, limit],
    queryFn: () => getEpisodes({ status: filter === 'all' ? undefined : filter, limit }),
  });

  const stats = episodes ? {
    total: episodes.total || 0,
    completed: episodes.completed_count || 0,
    processing: episodes.processing_count || 0,
  } : { total: 0, completed: 0, processing: 0 };

  const episodesList = episodes?.episodes || [];

  return (
    <div className="px-4 py-4 max-w-2xl mx-auto">
      <div className="hidden md:block mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Manage and track your podcast episodes</p>
      </div>

      <LastSyncBox />
      <StatsCards stats={stats} />

      <Tabs value={filter} onValueChange={(v) => {
        setFilter(v as typeof filter);
        setLimit(10);
      }} className="mb-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="all">All Episodes</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="processing">Processing</TabsTrigger>
        </TabsList>
      </Tabs>

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
          {limit < (stats.total || 0) && (
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
    </div>
  );
}
