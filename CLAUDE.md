# Podcast Analyzer

AI-driven podcast analysis platform that downloads, transcribes, cleans, and summarizes podcast episodes.

## Architecture

- **Backend**: Python/Flask REST API (`web/app.py`)
- **Frontend**: Next.js/React (`web-frontend/`)
- **Task Queue**: Celery + Redis for async processing
- **Database**: MongoDB for episode/feed storage
- **Observability**: Langfuse for prompt management and tracing
- **Logs**: Dozzle web UI for Docker log viewing

## Docker Services (docker-compose.yml)

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| mongodb | podcast_mongodb | 27017 | Document storage |
| redis | redis | 6380→6379 | Celery broker |
| web | podcast_web | 5002→5000 | Flask API server |
| worker | podcast_worker | — | Celery background tasks |
| feeder | podcast_feeder | — | Scheduled feed polling |
| dozzle | podcast_dozzle | 5001→8080 | Docker log viewer |
| web-frontend | podcast_web_frontend | 3000 | Next.js UI |

## Key Files

- `web/app.py` — Flask API (endpoints for episodes, feeds, summaries, Docker control)
- `tasks.py` — Celery task definitions (download, transcribe, summarize)
- `database.py` — MongoDB connection and queries
- `summarizer.py` — OpenAI GPT-4o-mini summarization logic
- `transcriber.py` — Whisper audio transcription
- `downloader.py` — Podcast audio download (YouTube compatible)
- `cleaner.py` — Transcript cleaning
- `scheduled_feeder.py` — Periodic feed polling service
- `feed_processor.py` — RSS/feed parsing
- `celery_app.py` — Celery app configuration
- `web-frontend/src/app/` — Next.js pages and components
- `web-frontend/src/lib/api.ts` — Frontend API client

## Commands

```bash
# Backend
pip install -r requirements.txt
python -m pytest                    # Run tests
flask --app web.app run --host=0.0.0.0  # Start Flask dev server

# Frontend
cd web-frontend
npm install
npm run build                       # Build Next.js
npm run dev                         # Dev server

# Docker
docker-compose up -d                # Start all services
docker-compose logs -f worker       # Follow worker logs
docker-compose restart worker       # Restart a service
```

## Environment Variables

See `.env` file (not committed). Key variables:
- `OPENAI_API_KEY` — OpenAI API for summarization
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST` — Observability
- `LANGFUSE_ENABLED` — Toggle Langfuse (default: false)
- `MONGO_CONNECTION_STRING` — MongoDB URI
- `FEEDER_INTERVAL_MINUTES` — Feed polling interval (default: 60)

## Production

Server path: `/home/podcast/podcast-summarizer`
All services run via `docker-compose up -d`.
Dozzle available at port 5001 for log viewing.
