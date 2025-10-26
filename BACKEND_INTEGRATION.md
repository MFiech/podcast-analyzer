# Backend API Integration Guide

**Status**: ✅ Complete and Ready for Production

---

## Quick Start

### 1. Start the Flask Backend
```bash
cd /Users/michalfiech/Coding/podcast-summarizer
python web/app.py
# Backend runs on http://localhost:5000
```

### 2. Start the Next.js Frontend
```bash
cd web-frontend
npm run dev
# Frontend runs on http://localhost:3000
```

### 3. Access the Application
- Frontend: http://localhost:3000
- API: http://localhost:5000/api/...

---

## API Endpoints

### Episodes

#### GET /api/episodes
List all episodes with optional filtering and pagination.

**Query Parameters:**
- `status`: Filter by status (completed, pending, processing)
- `limit`: Number of episodes per page (default: 10)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "episodes": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Episode Title",
      "url": "https://...",
      "feed_source": "Podcast Name",
      "duration": "45:32",
      "status": "completed",
      "summary": "AI Summary...",
      "transcript": "Full transcript...",
      "audio_path": "path/to/audio.mp3",
      "submitted_date": "2024-01-15",
      "completed_date": "2024-01-15"
    }
  ],
  "total": 127,
  "completed_count": 115,
  "processing_count": 3
}
```

#### GET /api/episodes/:id
Get a single episode by ID.

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "title": "Episode Title",
  ...
}
```

#### POST /api/episodes
Add a new episode for processing.

**Request Body:**
```json
{
  "url": "https://example.com/episode.mp3"
}
```

**Response:** `201 Created`

#### POST /api/episodes/:id/summarize-again
Re-run summarization on an existing episode.

**Response:**
```json
{
  "success": true,
  "message": "Episode queued for re-summarization"
}
```

---

### RSS Feeds

#### GET /api/feeds
List all RSS feeds.

**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "title": "Podcast Name",
    "url": "https://podcast.com/feed.xml",
    "episode_count": 42,
    "active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T12:30:00Z"
  }
]
```

#### POST /api/feeds
Add a new RSS feed.

**Request Body:**
```json
{
  "feed_url": "https://podcast.com/feed.xml",
  "feed_title": "Podcast Name",
  "custom_prompt": "Optional: Special instructions for AI"
}
```

**Response:** `201 Created`

#### PUT /api/feeds/:id
Update a feed.

**Request Body:**
```json
{
  "feed_url": "https://new-url.com/feed.xml",
  "feed_title": "New Title",
  "custom_prompt": "Updated instructions"
}
```

#### DELETE /api/feeds/:id
Delete a feed.

**Response:** `200 OK`

---

### Feeder Status

#### GET /api/feeder/status
Get feeder container status and last sync info.

**Response:**
```json
{
  "status": "running",
  "is_running": true,
  "last_run_status": "success",
  "last_run_time": "2024-01-15T12:30:00Z",
  "last_run_time_readable": "2 hours ago",
  "next_run_in_minutes": 28
}
```

#### POST /api/feeder/restart
Trigger immediate feed check.

**Response:**
```json
{
  "success": true,
  "message": "Feeder restarted - checking for new episodes"
}
```

---

## Data Format

### Episode Fields
| Field | Type | Description |
|-------|------|-------------|
| id | string | MongoDB ObjectId (converted to string) |
| title | string | Episode title |
| url | string | Episode/audio URL |
| feed_source | string | Podcast name |
| duration | string | Duration in MM:SS format |
| status | string | "completed", "pending", "processing", or "failed" |
| summary | string | AI-generated summary |
| transcript | string | Full transcript |
| raw_transcript | string | Raw transcript before cleaning |
| audio_path | string | Path to audio file in /data directory |
| submitted_date | string | Date episode was added |
| completed_date | string | Date processing completed |
| hidden | boolean | Whether episode is hidden from view |

### Feed Fields
| Field | Type | Description |
|-------|------|-------------|
| id | string | MongoDB ObjectId (converted to string) |
| title | string | Feed/podcast name |
| url | string | RSS feed URL |
| episode_count | number | Number of episodes from this feed |
| active | boolean | Whether feed is active |
| created_at | string | Feed creation timestamp |
| updated_at | string | Last update timestamp |

---

## CORS Configuration

The backend is configured to accept requests from any origin for API endpoints:

```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

This allows the frontend at `http://localhost:3000` to communicate with the backend at `http://localhost:5000`.

---

## Error Handling

All API errors follow a consistent format:

```json
{
  "error": "Error message describing the issue"
}
```

**Status Codes:**
- `200`: Success
- `201`: Created (new resource)
- `400`: Bad request (invalid input)
- `404`: Not found
- `409`: Conflict (duplicate entry)
- `500`: Server error

---

## Frontend Integration Points

The Next.js frontend connects to the backend through:

**API Client Location:** `/web-frontend/src/lib/api.ts`

**Configuration:**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';
```

**Environment Variable:**
- Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
- Default: `http://localhost:5000`

---

## Testing the API

### Using cURL

#### List episodes
```bash
curl http://localhost:5000/api/episodes
```

#### Get single episode
```bash
curl http://localhost:5000/api/episodes/507f1f77bcf86cd799439011
```

#### Add episode
```bash
curl -X POST http://localhost:5000/api/episodes \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/episode.mp3"}'
```

#### List feeds
```bash
curl http://localhost:5000/api/feeds
```

#### Add feed
```bash
curl -X POST http://localhost:5000/api/feeds \
  -H "Content-Type: application/json" \
  -d '{"feed_url":"https://podcast.com/feed.xml","feed_title":"My Podcast"}'
```

---

## Production Deployment

### Backend
1. Set `debug=False` in Flask app
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure appropriate CORS origins (not "*")
4. Use environment variables for sensitive config
5. Set up proper logging

### Frontend
1. Build the Next.js app: `npm run build`
2. Set `NEXT_PUBLIC_API_BASE_URL` to production backend URL
3. Deploy static files to CDN or hosting
4. Use appropriate caching headers

---

## Troubleshooting

### Frontend can't connect to backend
1. Check Flask is running: `http://localhost:5000/api/episodes`
2. Verify CORS headers are present in response
3. Check network tab in browser DevTools
4. Ensure `NEXT_PUBLIC_API_BASE_URL` is set correctly

### Episodes show as empty
1. Verify database connection in Flask
2. Check MongoDB is running
3. Add sample data or use "Manually Submit URL" feature

### API returns 500 error
1. Check Flask console for error messages
2. Verify database credentials
3. Ensure all required packages are installed

---

## Performance Notes

- Episodes list is paginated (10 per page by default)
- Feeds are cached in React Query for 5 minutes
- Episodes cache for 5 minutes before refetch
- Status endpoint for real-time feeder updates

---

**Last Updated**: October 26, 2025  
**Status**: Production Ready ✅
