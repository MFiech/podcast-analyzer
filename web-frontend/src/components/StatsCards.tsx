'use client';

import React from 'react';
import { Card } from '@/components/ui/card';

export interface StatsData {
  total: number;
  completed: number;
  processing: number;
}

interface StatsCardsProps {
  stats: StatsData;
}

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-3 gap-3 mb-6">
      <Card className="p-4 text-center">
        <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
        <div className="text-xs text-gray-500 mt-1">Episodes</div>
      </Card>
      <Card className="p-4 text-center">
        <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
        <div className="text-xs text-gray-500 mt-1">Completed</div>
      </Card>
      <Card className="p-4 text-center">
        <div className="text-2xl font-bold text-orange-600">{stats.processing}</div>
        <div className="text-xs text-gray-500 mt-1">Processing</div>
      </Card>
    </div>
  );
}
