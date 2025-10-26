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
import { MoreVertical, Settings, Info, Zap, ExternalLink, Github, BarChart3 } from 'lucide-react';

const navigationItems = [
  { href: '/', label: 'Episodes' },
  { href: '/feeds', label: 'RSS Feeds' },
];

const moreItems = [
  { label: 'Prompt Evals', icon: BarChart3, href: 'https://cloud.langfuse.com/project/cmh3umme800vzad075pjehiow', external: true },
  { label: 'Server Logs', icon: Info, href: 'http://localhost:5001/', external: true },
  { label: 'GitHub Repo', icon: Github, href: 'https://github.com/MFiech/podcast-analyzer', external: true },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 md:hidden border-t bg-white z-40 safe-area-inset-bottom">
        <div className="flex items-stretch justify-between h-16">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex-1 flex flex-col items-center justify-center gap-1 text-sm border-r last:border-r-0"
            >
              <span className={pathname === item.href ? 'text-blue-600 font-bold' : 'text-gray-600 font-semibold'}>
                {item.label}
              </span>
            </Link>
          ))}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex-1 h-16 rounded-none flex flex-col items-center justify-center gap-1 text-sm font-semibold">
                <span className="text-gray-600">More</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              {moreItems.map((item) => {
                const Icon = item.icon;
                return (
                  <DropdownMenuItem key={item.label} asChild>
                    <a href={item.href} target="_blank" rel="noopener noreferrer" className="flex cursor-pointer">
                      <Icon className="w-4 h-4 mr-2" />
                      <span>{item.label}</span>
                    </a>
                  </DropdownMenuItem>
                );
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Desktop Top Navigation */}
      <div className="hidden md:flex items-center justify-between px-6 py-4 border-b bg-white sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
            P
          </div>
          <span className="font-bold text-lg">Podcast Summarizer</span>
        </div>
        <nav className="flex gap-8 items-center">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`pb-2 border-b-2 font-bold text-base ${
                pathname === item.href
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-700 hover:text-gray-900'
              }`}
            >
              {item.label}
            </Link>
          ))}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="pb-2 border-b-2 border-transparent text-gray-700 hover:text-gray-900 font-bold text-base">
                More ⌄
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              {moreItems.map((item) => {
                const Icon = item.icon;
                return (
                  <DropdownMenuItem key={item.label} asChild>
                    <a href={item.href} target="_blank" rel="noopener noreferrer" className="flex cursor-pointer">
                      <Icon className="w-4 h-4 mr-2" />
                      <span>{item.label}</span>
                    </a>
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
