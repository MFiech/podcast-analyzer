import axios, { AxiosInstance } from 'axios';

// Determine API base URL at runtime based on current hostname
// This allows the app to work on both local development and VPS without rebuilding
const getApiBaseUrl = (): string => {
  // Server-side rendering: use environment variable fallback
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5002';
  }

  // Client-side: detect current hostname and use port 5002
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  return `${protocol}//${hostname}:5002`;
};

const apiClient: AxiosInstance = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Episode {
  id: string;
  title: string;
  url: string;
  feed_title: string;
  feed_source?: string;
  duration: number | string;
  status: 'completed' | 'processing' | 'failed' | 'pending';
  summary: string;
  transcript: string;
  raw_transcript?: string;
  file_path?: string;
  audio_path?: string;
  submitted_date?: string;
  completed_date?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Feed {
  id: string;
  title: string;
  url: string;
  episode_count: number;
  last_updated?: string;
  status?: 'active' | 'error';
  customPromptInstructions?: string;
}

export interface FeederStatus {
  status: string;
  is_running: boolean;
  last_run_status: string;
  last_run_time?: string;
  last_run_time_readable?: string;
  next_run_in_minutes?: number;
}

// Episodes
export const getEpisodes = async (filters?: {
  status?: string;
  limit?: number;
  offset?: number;
}) => {
  const response = await apiClient.get('/api/episodes', { params: filters });
  return response.data;
};

export const getEpisode = async (id: string) => {
  const response = await apiClient.get(`/api/episodes/${id}`);
  return response.data;
};

export const addEpisode = async (url: string) => {
  const response = await apiClient.post('/api/episodes', { url });
  return response.data;
};

export const summarizeAgain = async (episodeId: string) => {
  const response = await apiClient.post(`/api/episodes/${episodeId}/summarize-again`);
  return response.data;
};

export const hideEpisode = async (episodeId: string) => {
  const response = await apiClient.post(`/api/episodes/${episodeId}/hide`);
  return response.data;
};

export const restoreEpisode = async (episodeId: string) => {
  const response = await apiClient.post(`/api/episodes/${episodeId}/restore`);
  return response.data;
};

export const retryEpisode = async (episodeId: string) => {
  const response = await apiClient.post(`/api/episodes/${episodeId}/retry`);
  return response.data;
};

// Feeds
export const getFeeds = async () => {
  const response = await apiClient.get('/api/feeds');
  return response.data;
};

export const addFeed = async (data: {
  feed_url: string;
  feed_title: string;
  custom_prompt?: string;
}) => {
  const response = await apiClient.post('/api/feeds', data);
  return response.data;
};

export const updateFeed = async (feedId: string, data: {
  feed_url: string;
  feed_title: string;
  custom_prompt?: string;
}) => {
  const response = await apiClient.put(`/api/feeds/${feedId}`, data);
  return response.data;
};

export const deleteFeed = async (feedId: string) => {
  const response = await apiClient.delete(`/api/feeds/${feedId}`);
  return response.data;
};

// Feeder status
export const getFeederStatus = async (): Promise<FeederStatus> => {
  const response = await apiClient.get('/api/feeder/status');
  return response.data;
};

export const restartFeeder = async () => {
  const response = await apiClient.post('/api/feeder/restart');
  return response.data;
};

export default apiClient;
