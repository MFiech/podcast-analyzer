# Podcast Summarizer - UI Revamp Implementation Plan

## Overview
Transform the current Flask + Jinja2 frontend into a modern Next.js + React + shadcn/ui single-page application. The Flask backend remains unchanged and serves as the API layer.

---

## Phase 1: Project Setup & Infrastructure

### 1.1 Create Next.js Frontend Project
- Initialize new Next.js project in `/web-frontend/` directory (parallel to existing `/web/` Flask app)
- Configuration:
  - Framework: Next.js 14+ (App Router)
  - Language: TypeScript
  - CSS: Tailwind CSS (required for shadcn/ui)
  - Package Manager: npm/yarn
  
### 1.2 Install Dependencies
- shadcn/ui components (via CLI)
- React Query (for API data fetching)
- Axios (HTTP client for Flask API communication)
- React Hot Toast or Sonner (toast notifications, shadcn provides Sonner)
- Required shadcn Components to install:
  - Tabs, Card, Button, Input, Textarea, Badge
  - Dialog, Drawer, Dropdown Menu
  - Accordion, Scroll Area, Separator
  - Toast/Toaster (Sonner integration)
  - Skeleton (loading states)
  - Form (React Hook Form integration)

### 1.3 Configure Flask Backend as API
- Update Flask `app.py` to serve JSON API endpoints (already partially done)
- Add CORS middleware to allow frontend requests
- Ensure endpoints return proper JSON responses
- Main endpoints needed:
  - `GET /api/episodes` - list episodes with filters
  - `GET /api/episodes/<id>` - single episode details
  - `POST /api/episodes` - add new episode
  - `POST /api/episodes/<id>/summarize-again` - retry summarization
  - `GET /api/feeds` - list RSS feeds
  - `POST /api/feeds` - add new feed
  - `PUT /api/feeds/<id>` - edit feed
  - `DELETE /api/feeds/<id>` - delete feed
  - `GET /api/feeder/status` - sync status (already exists)

---

## Phase 2: Core Navigation & Layout

### 2.1 Responsive Navigation Component
**File**: `/web-frontend/src/components/Navigation.tsx`

Structure:
- **Mobile (< 768px)**:
  - Fixed bottom navigation bar using shadcn `Tabs`
  - Three tabs: Dashboard (icon), RSS Feeds (icon), More (icon)
  - Height: ~60px, safe area padding
  
- **Desktop (≥ 768px)**:
  - Hidden mobile nav
  - Top horizontal navigation
  - Side-by-side layout with icons + labels

Implementation approach:
- Single Tabs component with responsive CSS (`md:` Tailwind breakpoint)
- Use `Tabs` component with `TabsList` (bottom-aligned on mobile, top-aligned on desktop)
- Tab values: "dashboard", "feeds", "more"
- Use icons from lucide-react (already included with shadcn)

### 2.2 Root Layout Component
**File**: `/web-frontend/src/app/layout.tsx`

Structure:
- Global navigation wrapper
- Content area (scrollable)
- Account/notifications icon in top-right header on both mobile & desktop
- App header: Logo icon + "Podcast Summarizer" text + notification bell

---

## Phase 3: Dashboard Screen (Mobile-First)

### 3.1 Dashboard Page Component
**File**: `/web-frontend/src/app/dashboard/page.tsx`

Mobile Layout (375px reference):
```
[Header: Logo + Title + Bell Icon]
────────────────────────────────────
[Last Sync Info Box - Info Badge styled]
  Last sync: [date/time] | "Check for new episodes" link
────────────────────────────────────
[Stats Cards - 3 columns]
  24 Episodes | 18 Completed | 3 Processing
────────────────────────────────────
[Filter Tabs]
  All Episodes | Completed | Processing
────────────────────────────────────
[Episodes List - scrollable]
  [Episode Card 1]
  [Episode Card 2]
  ...
────────────────────────────────────
[Load More Button or infinite scroll]
────────────────────────────────────
[Bottom Navigation]
```

Components to build:
- **LastSyncBox** - Uses shadcn `Alert` component with info icon, shows sync time + "Check for new episodes" link
- **StatsCards** - Three `Card` components in flexbox grid (3 equal cols)
- **FilterTabs** - shadcn `Tabs` for "All Episodes", "Completed", "Processing"
- **EpisodeCard** - Clickable card with:
  - Episode title (bold, clickable → detail view)
  - Feed source + RSS icon
  - Duration (MM:SS)
  - Status badge (shadcn `Badge` with appropriate color)
  - Submission date (gray text)
  - Vertical dropdown menu (three dots) using shadcn `DropdownMenu`
- **PaginationButton** - "Load More Episodes" button at bottom

### 3.2 Episode Card Details
- Hover state: subtle shadow increase
- Tap/click: navigate to `/episode/<id>` detail view
- Dropdown menu actions:
  - Hide episode
  - Retry (if failed)
  - Delete (if applicable)

---

## Phase 4: Episode Detail Screen ✅ COMPLETED

### 4.1 Episode Detail Page ✅
**File**: `/web-frontend/src/app/episode/[id]/page.tsx`
- ✅ Back button (left) + Episode title (center) + Hamburger menu (right)
- ✅ Episode metadata (feed source, duration, date)
- ✅ AI Summary section with status badge
- ✅ Completed/Processing/Failed state indicators
- ✅ Full Transcript accordion (collapsible by default)

### 4.2 Components Built ✅
- ✅ **AudioPlayer** (`src/components/AudioPlayer.tsx`) - HTML5 audio player with:
  - Play/pause button with icons
  - Progress bar (Slider component)
  - Current time / Total duration display
  - Volume control
  - Fixed positioning on mobile (bottom-20), relative on desktop
  - Responsive design
- ✅ **EpisodeMenu** (`src/components/EpisodeMenu.tsx`) - Hamburger dropdown with "Summarize Again" action

### 4.3 Features ✅
- ✅ React Query data fetching
- ✅ Sticky header with back navigation
- ✅ Loading states with Skeleton loaders
- ✅ Error handling
- ✅ Status-based UI rendering
- ✅ Toast notifications on actions

### 4.1 Episode Detail Page
**File**: `/web-frontend/src/app/episode/[id]/page.tsx`

Mobile Layout Structure:
```
[Header: App Logo + Title + Bell Icon]
[Back Button < | Episode Title | Hamburger ...]
════════════════════════════════════
[Scrollable Content Area]
  Episode metadata row
  (Feed source, Duration, Status badge, Date)
  
  "AI Summary" section with status badge
  
  [Summary Content Box]
    - Rich markdown formatting support
    - Collapsible sections if needed
  
  [Full Transcript Accordion]
    - Collapsed by default
    - "Full Transcript (42 min remaining)" header
    - Timestamps + speaker names + text
    - "Show Full Transcript" expandable link
════════════════════════════════════
[Fixed/Pinned Audio Player - Bottom]
  Play button | Progress bar | Time (02:35 / 45:32) | Volume
```

Components to build:
- **Back Navigation** - Back button (left) + title (center) + hamburger menu button (right)
- **EpisodeHeader** - Feed, duration, status, date metadata
- **SummarySection** - Markdown rendered summary with rich formatting
- **TranscriptAccordion** - shadcn `Accordion` with transcript entries
  - Each entry: timestamp + speaker name + text
  - Collapsible by default
  - "Show Full Transcript" link at bottom
- **AudioPlayer** - Fixed/sticky at bottom:
  - HTML5 `<audio>` element with custom controls
  - Play/pause button (shadcn `Button` with icon)
  - Progress bar (shadcn `Slider` component)
  - Current time / Total duration
  - Volume control
  - Responsive: full width on mobile, centered on desktop

### 4.2 Hamburger Menu (Episode Detail)
**File**: `/web-frontend/src/components/EpisodeMenu.tsx`

- shadcn `DropdownMenu` component
- Single action: "Summarize Again"
- Triggers re-summarization API call
- Shows toast notification on success/error

---

## Phase 5: RSS Feeds Management Screen

### 5.1 Feeds List Page
**File**: `/web-frontend/src/app/feeds/page.tsx`

Mobile Layout:
```
[Header: App Logo + Title + Bell Icon]
════════════════════════════════════
[Title: "RSS Feeds" | "5 active feeds"]
────────────────────────────────────
[Feeds List - scrollable]
  [Feed Card 1]
  [Feed Card 2]
  ...
────────────────────────────────────
[Info Box]
  "Adding RSS Feeds"
  Helper text about RSS URLs
════════════════════════════════════
[Floating Action Button - "+" centered bottom right]
[Bottom Navigation]
```

Components to build:
- **FeedsHeader** - "RSS Feeds" title + counter "5 active feeds"
- **FeedCard** - Each card displays:
  - Status indicator dot (green/orange/red)
  - Feed title (bold)
  - Feed URL (gray, smaller)
  - Stats: "12 episodes | Last updated: 2h ago"
  - Vertical dropdown menu (three dots) using shadcn `DropdownMenu`
- **InfoBox** - shadcn `Alert` with info icon, instructions for adding feeds
- **FloatingActionButton** - Large blue button with "+" icon, sticky positioned at bottom-right
  - Opens Add Feed modal/drawer on click

### 5.2 Feed Card Dropdown Menu
- **Edit** - Opens edit drawer/modal
- **Delete** - Shows confirmation dialog

### 5.3 Add/Edit Feed Modal/Drawer
**File**: `/web-frontend/src/components/FeedModal.tsx`

Behavior:
- **Mobile**: Bottom drawer using shadcn `Drawer`
- **Desktop**: Modal using shadcn `Dialog`
- Conditional rendering based on `useMediaQuery` hook

Form fields:
- Feed URL (required, text input using shadcn `Input`)
- Feed Title (optional, text input)
- Custom Prompt Instructions (optional, using shadcn `Textarea`)
- Buttons: "Cancel" + "Add Feed" / "Update Feed"

---

## Phase 6: More Menu Screen

### 6.1 More Screen Page
**File**: `/web-frontend/src/app/more/page.tsx`

Mobile Layout:
```
[Header: App Logo + Title + Bell Icon]
════════════════════════════════════
[Quick Actions Section]
  [Link Item - "Manually Submit URL"]
    Icon | Text | Chevron >
────────────────────────────────────
[Account & Settings Section]
  [Link Item - "Profile Settings"]
  [Link Item - "Notifications"]
  [Link Item - "Sync Settings"]
────────────────────────────────────
[External Links Section]
  [Link Item - "Service Logs"] (opens in new tab, external icon)
  [Link Item - "Prompt Evaluations"] (opens in new tab)
  [Link Item - "GitHub Repository"] (opens in new tab)
────────────────────────────────────
[Usage Statistics Section]
  [Stat Cards - 2x2 grid]
    127 Episodes Processed | 45h Audio Analyzed
    5.2k Words Summarized | 98% Success Rate
────────────────────────────────────
[App Information Section]
  Version | Privacy Policy | Terms of Service
════════════════════════════════════
[Bottom Navigation]
```

Components to build:
- **MenuSectionHeader** - Section titles with subtle styling
- **MenuLinkItem** - Reusable component for each menu item
  - Icon (left)
  - Title + subtitle text (center)
  - Chevron or external link icon (right)
  - Tap/click handler
- **StatisticsGrid** - 2x2 grid of stat cards using shadcn `Card`
- **ExternalLink** - Menu items with external icon, opens in `target="_blank"`

### 6.2 Manually Submit URL Modal/Drawer
**File**: `/web-frontend/src/components/SubmitUrlModal.tsx`

- Triggered from "Manually Submit URL" menu item
- Mobile: Bottom drawer, Desktop: Modal
- Form fields:
  - URL input (text field using shadcn `Input`)
  - Button: "Queue for Analysis"
- On submit: POST to Flask API, show success toast

---

## Phase 7: Styling & Responsive Design

### 7.1 Breakpoints & Tailwind Configuration
```
Mobile:   < 768px  (default, base styles)
Tablet:   768px - 1024px
Desktop:  ≥ 1024px
```

### 7.2 Desktop Adaptations
- **Navigation**: Convert bottom tabs to top horizontal bar
- **Layouts**: Adjust card grids for wider screens
- **Modals**: Convert drawers to centered modals
- **Audio Player**: Center on screen, width constraint

### 7.3 Color Scheme & Theme
- Use shadcn's default theme (light/dark compatible)
- Status badge colors:
  - Completed: Green
  - Processing: Orange/Yellow
  - Failed: Red
- Primary action buttons: Blue
- Link colors: Blue with hover underline

---

## Phase 8: API Integration

### 8.1 API Service Layer
**File**: `/web-frontend/src/lib/api.ts`

Implement helper functions:
- `getEpisodes(filters?)`
- `getEpisode(id)`
- `addEpisode(url)`
- `summarizeAgain(episodeId)`
- `getFeeds()`
- `addFeed(url, title, prompt)`
- `updateFeed(id, url, title, prompt)`
- `deleteFeed(id)`
- `getFeederStatus()`
- `submitUrl(url)`

### 8.2 React Query Setup
**File**: `/web-frontend/src/lib/queryClient.ts`

- Configure React Query with appropriate cache times
- Error handling & retry logic
- Loading states for UI

### 8.3 Environment Variables
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

---

## Phase 9: Testing & Validation

### 9.1 Responsive Testing
- Test on actual mobile device (375px)
- Test on tablet (768px)
- Test on desktop (1920px)
- Verify bottom nav on mobile, top nav on desktop

### 9.2 Functionality Testing
- Navigation between tabs works
- Episode cards clickable, navigate to detail
- Audio player playback functions
- Forms submit correctly to Flask API
- Error states handled with toasts

### 9.3 Browser Compatibility
- Chrome, Safari, Firefox (latest versions)
- Mobile browsers on iOS/Android

---

## Phase 10: Deployment Considerations

### 10.1 Build Process
- Next.js static generation where possible
- API routes proxy to Flask backend (optional)

### 10.2 File Structure
```
/podcast-summarizer/
├── web/                    # Existing Flask backend (unchanged)
│   ├── app.py
│   ├── templates/
│   └── static/
├── web-frontend/           # New Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/
│   │   │   ├── episode/
│   │   │   ├── feeds/
│   │   │   └── more/
│   │   ├── components/
│   │   │   ├── Navigation.tsx
│   │   │   ├── EpisodeCard.tsx
│   │   │   ├── AudioPlayer.tsx
│   │   │   ├── FeedModal.tsx
│   │   │   └── ...
│   │   └── lib/
│   │       ├── api.ts
│   │       └── queryClient.ts
│   ├── package.json
│   └── next.config.ts
└── database.py             # Backend unchanged
```

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|-----------------|
| 1 | Setup & Dependencies | 1-2 hours |
| 2 | Navigation & Layout | 2-3 hours |
| 3 | Dashboard Screen | 3-4 hours |
| 4 | Episode Detail Screen | 3-4 hours |
| 5 | Feeds Management | 2-3 hours |
| 6 | More Menu | 2-3 hours |
| 7 | Styling & Responsive | 2-3 hours |
| 8 | API Integration | 2-3 hours |
| 9 | Testing & Validation | 2-3 hours |
| **Total** | | **19-28 hours** |

---

## Key Design Decisions

1. **Separate Frontend**: Next.js frontend lives in `/web-frontend/`, Flask backend remains in `/web/`
2. **shadcn/ui Only**: All UI components from shadcn/ui library
3. **HTML5 Audio**: Simple native player, no external audio library
4. **Mobile-First**: Base styles for mobile, scale up with Tailwind breakpoints
5. **TypeScript**: Full type safety throughout
6. **API-Driven**: Frontend communicates with Flask via REST API

---

## Notes for Implementation

- All components should follow shadcn/ui patterns and conventions
- Use Tailwind CSS for responsive design, no custom CSS unless necessary
- Implement proper error boundaries and loading states
- Add toast notifications for user feedback (using Sonner from shadcn)
- Ensure accessibility (ARIA labels, keyboard navigation)
- Consider dark mode support (shadcn provides this)

