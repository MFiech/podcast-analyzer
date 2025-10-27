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
import ReactMarkdown from 'react-markdown';

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
    <div className="pb-40 md:pb-32">
      <div className="sticky top-0 md:top-16 bg-white border-b z-30">
        <div className="px-4 py-4 max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-3 gap-2">
            <Button variant="ghost" size="icon" onClick={() => router.back()} className="h-10 w-10 -ml-2 flex-shrink-0">
              <ChevronLeft className="w-6 h-6" />
            </Button>
            <EpisodeMenu episodeId={episodeId} />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 leading-tight">{episode.title}</h1>
          <p className="text-sm text-gray-600 mt-2">📡 {episode.feed_title || episode.feed_source || 'Unknown'}</p>
        </div>
      </div>

      <div className="px-4 py-6 max-w-4xl mx-auto">
        <h2 className="text-lg font-bold text-gray-900 mb-4">AI Summary</h2>

        {episode.status === 'completed' && episode.summary ? (
          <div className="mb-8 p-6 bg-gray-50 rounded-lg">
            <div className="prose prose-md dark:prose-invert max-w-none text-gray-700 leading-relaxed [&_p]:mb-4 [&_p]:last:mb-0 [&_ul]:mb-4 [&_li]:mb-2 [&_h1]:text-lg [&_h2]:text-base [&_h3]:text-sm">
              <ReactMarkdown>
                {episode.summary}
              </ReactMarkdown>
            </div>
          </div>
        ) : episode.status === 'processing' ? (
          <div className="mb-8 p-6 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-orange-700 text-base">⏳ Processing... This usually takes a few minutes.</p>
          </div>
        ) : episode.status === 'failed' ? (
          <div className="mb-8 p-6 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-base">❌ Summarization failed. Please try again.</p>
          </div>
        ) : null}

        {episode.transcript && (
          <Accordion type="single" collapsible className="mb-24 md:mb-6">
            <AccordionItem value="item-1">
              <AccordionTrigger className="hover:no-underline">
                <h2 className="text-lg font-bold text-gray-900">Full Transcript</h2>
              </AccordionTrigger>
              <AccordionContent>
                <div className="p-6 bg-gray-50 rounded-lg mt-4 text-gray-700 whitespace-pre-wrap text-base leading-relaxed">
                  {episode.transcript}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        )}
      </div>

      {(episode.audio_path || episode.file_path) && (
        <AudioPlayer
          audioUrl={`${typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:5002` : 'http://localhost:5002'}/data/${episode.audio_path || episode.file_path}`}
          title={episode.title}
        />
      )}
    </div>
  );
}
