'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreVertical, Settings, Info, Zap } from 'lucide-react';

const navigationItems = [
  { href: '/', label: 'Episodes', icon: '📊' },
  { href: '/feeds', label: 'RSS Feeds', icon: '📡' },
];

const moreItems = [
  { label: 'Settings', icon: Settings },
  { label: 'About', icon: Info },
  { label: 'Usage Stats', icon: Zap },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 md:hidden border-t bg-white z-40 safe-area-inset-bottom">
        <div className="flex items-center justify-around h-16">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex flex-col items-center justify-center w-full h-full gap-1 text-xs"
            >
              <span className="text-xl">{item.icon}</span>
              <span className={pathname === item.href ? 'text-blue-600' : 'text-gray-600'}>
                {item.label}
              </span>
            </Link>
          ))}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="flex flex-col items-center justify-center">
                <span className="text-xl">☰</span>
                <span className="text-xs text-gray-600">More</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              {moreItems.map((item) => {
                const Icon = item.icon;
                return (
                  <DropdownMenuItem key={item.label}>
                    <Icon className="w-4 h-4 mr-2" />
                    <span>{item.label}</span>
                  </DropdownMenuItem>
                );
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
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
        </div>
        <nav className="flex gap-8 items-center">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 pb-2 border-b-2 ${
                pathname === item.href
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreVertical className="w-5 h-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              {moreItems.map((item) => {
                const Icon = item.icon;
                return (
                  <DropdownMenuItem key={item.label}>
                    <Icon className="w-4 h-4 mr-2" />
                    <span>{item.label}</span>
                  </DropdownMenuItem>
                );
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        </nav>
      </div>
    </>
  );
}
