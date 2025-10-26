'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';

const navigationItems = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/feeds', label: 'RSS Feeds', icon: '📡' },
  { href: '/more', label: 'More', icon: '☰' },
];

export function Navigation() {
  const pathname = usePathname();
  
  // Determine current tab
  const currentTab = navigationItems.find(item => 
    pathname.startsWith(item.href)
  )?.href || '/dashboard';

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 md:hidden border-t bg-white z-40 safe-area-inset-bottom">
        <Tabs value={currentTab} defaultValue="/dashboard" className="w-full">
          <TabsList className="w-full grid grid-cols-3 gap-0 rounded-none h-16 bg-white">
            {navigationItems.map((item) => (
              <TabsTrigger
                key={item.href}
                value={item.href}
                asChild
                className="rounded-none flex flex-col items-center justify-center h-full"
              >
                <Link href={item.href} className="flex flex-col items-center justify-center w-full h-full">
                  <span className="text-xl mb-1">{item.icon}</span>
                  <span className="text-xs">{item.label}</span>
                </Link>
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {/* Desktop Top Navigation */}
      <div className="hidden md:flex items-center justify-between px-6 py-4 border-b bg-white sticky top-0 z-40">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
              🎙️
            </div>
            <span className="font-bold text-lg">Podcast Summarizer</span>
          </div>
          <nav className="flex gap-8">
            {navigationItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 pb-2 border-b-2 ${
                  pathname.startsWith(item.href)
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>
        <Button variant="ghost" size="icon">
          <Bell className="w-5 h-5" />
        </Button>
      </div>
    </>
  );
}
