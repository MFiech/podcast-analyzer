'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useRouter } from 'next/navigation';
import { getEpisode } from '@/lib/api';
import { AudioPlayer } from '@/components/AudioPlayer';
import { EpisodeMenu } from '@/components/EpisodeMenu';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ChevronLeft } from 'lucide-react';

const statusConfig = {
  completed: { label: 'Completed', color: 'bg-green-100 text-green-800' },
  processing: { label: 'Processing', color: 'bg-orange-100 text-orange-800' },
  failed: { label: 'Failed', color: 'bg-red-100 text-red-800' },
};

export default function EpisodeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const episodeId = params.id as string;

  const { data: episode, isLoading, error } = useQuery({
    queryKey: ['episode', episodeId],
    queryFn: () => getEpisode(episodeId),
    enabled: !!episodeId,
  });

  if (isLoading) {
    return (
      <div className="px-4 py-4 max-w-2xl mx-auto pb-32">
        <Skeleton className="h-10 w-20 mb-4" />
        <Skeleton className="h-8 w-full mb-4" />
        <Skeleton className="h-40 w-full mb-4" />
      </div>
    );
  }

  if (error || !episode) {
    return (
      <div className="px-4 py-4 max-w-2xl mx-auto text-center py-12">
        <p className="text-red-600">Episode not found</p>
        <Button onClick={() => router.back()} className="mt-4">Go Back</Button>
      </div>
    );
  }

  const statusInfo = statusConfig[episode.status as keyof typeof statusConfig];
  
  // Helper functions to format data
  const formatDuration = (seconds: number | string) => {
    if (typeof seconds === 'string') return seconds;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${String(secs).padStart(2, '0')}`;
  };
  
  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return 'Unknown';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="pb-40">
      <div className="sticky top-0 md:top-16 bg-white border-b z-30">
        <div className="px-4 py-3 max-w-2xl mx-auto flex items-center justify-between">
          <Button variant="ghost" size="icon" onClick={() => router.back()} className="h-10 w-10 -ml-2">
            <ChevronLeft className="w-6 h-6" />
          </Button>
          <h1 className="flex-1 text-lg font-semibold line-clamp-1 px-2">{episode.title}</h1>
          <EpisodeMenu episodeId={episodeId} />
        </div>
      </div>

      <div className="px-4 py-4 max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-4 text-sm text-gray-600">
          <span>📡 {episode.feed_title || episode.feed_source || 'Unknown'}</span>
          <span>•</span>
          <span>⏱️ {formatDuration(episode.duration)}</span>
          <span>•</span>
          <span>{formatDate(episode.created_at || episode.submitted_date)}</span>
        </div>

        <div className="flex items-center gap-3 mb-6">
          <h2 className="text-lg font-semibold">AI Summary</h2>
          <Badge variant="secondary" className={statusInfo.color}>{statusInfo.label}</Badge>
        </div>

        {episode.status === 'completed' && episode.summary ? (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">{episode.summary}</p>
          </div>
        ) : episode.status === 'processing' ? (
          <div className="mb-6 p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-orange-700 text-sm">⏳ Processing... This usually takes a few minutes.</p>
          </div>
        ) : episode.status === 'failed' ? (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm">❌ Summarization failed. Please try again.</p>
          </div>
        ) : null}

        {episode.transcript && (
          <Accordion type="single" collapsible defaultValue="item-1" className="mb-6">
            <AccordionItem value="item-1">
              <AccordionTrigger className="hover:no-underline">
                <span className="font-semibold">Full Transcript</span>
              </AccordionTrigger>
              <AccordionContent>
                <div className="text-sm text-gray-700 whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {episode.transcript}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        )}
      </div>

      {(episode.audio_path || episode.file_path) && (
        <AudioPlayer
          audioUrl={`${process.env.NEXT_PUBLIC_API_BASE_URL}/data/${episode.audio_path || episode.file_path}`}
          title={episode.title}
        />
      )}
    </div>
  );
}
