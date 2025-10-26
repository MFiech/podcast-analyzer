'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from '@/components/ui/drawer';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useMediaQuery } from '@/lib/hooks/useMediaQuery';
import { useMutation } from '@tanstack/react-query';
import { addEpisode } from '@/lib/api';
import { toast } from 'sonner';
import { Link2, Bell, Settings, Users, FileText, Gauge, Info, Lock, ExternalLink } from 'lucide-react';

export default function MorePage() {
  const isDesktop = useMediaQuery('(min-width: 768px)');
  const [isUrlModalOpen, setIsUrlModalOpen] = useState(false);
  const [urlInput, setUrlInput] = useState('');

  const { mutate: handleSubmitUrl, isPending } = useMutation({
    mutationFn: (url: string) => addEpisode(url),
    onSuccess: () => {
      toast.success('Episode queued for analysis');
      setUrlInput('');
      setIsUrlModalOpen(false);
    },
    onError: () => {
      toast.error('Failed to submit episode');
    },
  });

  const UrlModalContent = () => (
    <div className="space-y-4">
      <div>
        <Label htmlFor="episode-url">Episode URL</Label>
        <Input
          id="episode-url"
          placeholder="https://example.com/episode.mp3"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
        />
      </div>
      <Button onClick={() => handleSubmitUrl(urlInput)} disabled={isPending || !urlInput.trim()} className="w-full">
        {isPending ? 'Queuing...' : 'Queue for Analysis'}
      </Button>
    </div>
  );

  return (
    <div className="px-4 py-4 max-w-2xl mx-auto pb-20 md:pb-0">
      <div className="hidden md:block mb-6">
        <h1 className="text-3xl font-bold text-gray-900">More</h1>
        <p className="text-gray-600 mt-1">Additional options and settings</p>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setIsUrlModalOpen(true)}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
              <Link2 className="w-5 h-5 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">Manually Submit URL</h3>
              <p className="text-sm text-gray-600">Add a single episode URL for analysis</p>
            </div>
            <ExternalLink className="w-5 h-5 text-gray-400 flex-shrink-0" />
          </div>
        </Card>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Account & Settings</h2>
        <div className="space-y-3">
          <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                <Users className="w-5 h-5 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">Profile Settings</h3>
                <p className="text-sm text-gray-600">Manage your account preferences</p>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 flex-shrink-0" />
            </div>
          </Card>
          <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                <Bell className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">Notifications</h3>
                <p className="text-sm text-gray-600">Configure alert preferences</p>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 flex-shrink-0" />
            </div>
          </Card>
          <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0">
                <Settings className="w-5 h-5 text-orange-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">Sync Settings</h3>
                <p className="text-sm text-gray-600">Manage automatic feed updates</p>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 flex-shrink-0" />
            </div>
          </Card>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">External Links</h2>
        <div className="space-y-3">
          {[
            { title: 'Service Logs', desc: 'View processing logs and errors', icon: FileText },
            { title: 'Prompt Evaluations', desc: 'Review AI prompt performance', icon: Gauge },
            { title: 'GitHub Repository', desc: 'View source code and contribute', icon: Users },
          ].map((link) => {
            const Icon = link.icon;
            return (
              <Card key={link.title} className="p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-gray-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{link.title}</h3>
                    <p className="text-sm text-gray-600">{link.desc}</p>
                  </div>
                  <ExternalLink className="w-5 h-5 text-gray-400 flex-shrink-0" />
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Usage Statistics</h2>
        <div className="grid grid-cols-2 gap-3">
          <Card className="p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">127</p>
            <p className="text-xs text-gray-600 mt-1">Episodes Processed</p>
          </Card>
          <Card className="p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">45h</p>
            <p className="text-xs text-gray-600 mt-1">Audio Analyzed</p>
          </Card>
          <Card className="p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">5.2k</p>
            <p className="text-xs text-gray-600 mt-1">Words Summarized</p>
          </Card>
          <Card className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">98%</p>
            <p className="text-xs text-gray-600 mt-1">Success Rate</p>
          </Card>
        </div>
      </div>

      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">App Information</h2>
        <div className="space-y-3">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Info className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Version</h3>
                <p className="text-sm text-gray-600">v2.1.4 (Build 2024.01)</p>
              </div>
            </div>
          </Card>
          <Card className="p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                <Lock className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">Privacy Policy</h3>
                <p className="text-sm text-gray-600">How we protect your data</p>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400" />
            </div>
          </Card>
          <Card className="p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">Terms of Service</h3>
                <p className="text-sm text-gray-600">Usage terms and conditions</p>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400" />
            </div>
          </Card>
        </div>
      </div>

      {isDesktop ? (
        <Dialog open={isUrlModalOpen} onOpenChange={setIsUrlModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Manually Submit Episode URL</DialogTitle>
              <DialogDescription>Add a single episode URL for analysis</DialogDescription>
            </DialogHeader>
            <UrlModalContent />
          </DialogContent>
        </Dialog>
      ) : (
        <Drawer open={isUrlModalOpen} onOpenChange={setIsUrlModalOpen}>
          <DrawerContent>
            <DrawerHeader>
              <DrawerTitle>Manually Submit Episode URL</DrawerTitle>
              <DrawerDescription>Add a single episode URL for analysis</DrawerDescription>
            </DrawerHeader>
            <div className="px-4 pb-4">
              <UrlModalContent />
            </div>
          </DrawerContent>
        </Drawer>
      )}
    </div>
  );
}
