'use client';

import React from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Clock } from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getFeederStatus, restartFeeder } from '@/lib/api';
import { toast } from 'sonner';

export function LastSyncBox() {
  const { data: status, refetch } = useQuery({
    queryKey: ['feederStatus'],
    queryFn: getFeederStatus,
  });

  const { mutate: checkForNew, isPending } = useMutation({
    mutationFn: restartFeeder,
    onSuccess: () => {
      toast.success('Checking for new episodes...');
      refetch();
    },
    onError: (error) => {
      toast.error('Failed to check for new episodes');
    },
  });

  return (
    <Alert className="mb-6 bg-blue-50 border-blue-200">
      <Clock className="h-4 w-4 text-blue-600" />
      <AlertDescription className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <span className="text-sm">
          Last sync: <span className="font-medium">{status?.last_run_time_readable || 'Never'}</span>
        </span>
        <Button
          variant="link"
          size="sm"
          onClick={() => checkForNew()}
          disabled={isPending}
          className="text-blue-600 hover:text-blue-700 p-0 h-auto whitespace-nowrap"
        >
          {isPending ? 'Checking...' : 'Check for new'}
        </Button>
      </AlertDescription>
    </Alert>
  );
}
