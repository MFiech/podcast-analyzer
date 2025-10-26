# Testing Setup: Frontend (port 3000) + Docker Backend (port 5002)

## Architecture Overview

```
┌─────────────────────────────────────┐
│  Next.js Frontend (Port 3000)       │
│  http://localhost:3000              │
└──────────────┬──────────────────────┘
               │ HTTP API calls
               ▼
┌─────────────────────────────────────┐
│  Docker Container (pod_web)         │
│  Flask Backend (Port 5002)          │
│  (maps to internal port 5000)       │
└──────────────┬──────────────────────┘
               │ Connects to
               ▼
┌─────────────────────────────────────┐
│  MongoDB Container (port 27017)     │
│  Redis Container (port 6380)        │
└─────────────────────────────────────┘
```

## Port Mapping

| Service | Internal Port | Host Port | URL |
|---------|---------------|-----------|-----|
| MongoDB | 27017 | 27017 | `mongodb://localhost:27017` |
| Redis | 6379 | 6380 | `localhost:6380` |
| Flask BE | 5000 | 5002 | `http://localhost:5002` |
| Next.js FE | 3000 | 3000 | `http://localhost:3000` |
| Dozzle (logs) | 8080 | 5001 | `http://localhost:5001` |

## Setup & Testing

### Step 1: Start Docker Containers

```bash
cd /Users/michalfiech/Coding/podcast-summarizer
docker-compose up -d
```

This starts:
- ✅ MongoDB (port 27017)
- ✅ Redis (port 6380)
- ✅ Flask Backend (port 5002) - `podcast_web`
- ✅ Celery Worker - `podcast_worker`
- ✅ Feeder Service - `podcast_feeder`
- ✅ Dozzle (logs viewer) - port 5001

### Step 2: Verify Backend is Running

```bash
# Check Docker containers
docker ps | grep podcast

# Test API endpoint
curl http://localhost:5002/api/episodes
```

Expected response: JSON array of episodes (or empty array if no data)

### Step 3: Start Next.js Frontend

```bash
cd web-frontend
npm run dev
```

Frontend should start on `http://localhost:3000`

### Step 4: Test Integration

1. **Open browser**: http://localhost:3000
2. **Check Network Tab** (DevTools):
   - Requests should go to `http://localhost:5002/api/...`
   - Look for status 200 responses
3. **Test Features**:
   - Dashboard page should load (may be empty if no data)
   - RSS Feeds page should load
   - More menu should load
   - Check browser console for any CORS errors

### Step 5: Monitor Backend Logs

```bash
# View all Docker logs
docker-compose logs -f

# View only Flask backend logs
docker-compose logs -f podcast_web

# View Dozzle web interface
# Open: http://localhost:5001
```

## Configuration Details

### Frontend Environment

**File**: `web-frontend/.env.local`

```
# Docker Backend Configuration
# The Flask backend runs in Docker on port 5002 (mapped from internal port 5000)
NEXT_PUBLIC_API_BASE_URL=http://localhost:5002
```

**To switch backends** (if needed):
- Docker: `NEXT_PUBLIC_API_BASE_URL=http://localhost:5002`
- Local: `NEXT_PUBLIC_API_BASE_URL=http://localhost:5000`

Then restart the Next.js dev server: `npm run dev`

### Backend Configuration

**Docker Compose**: `docker-compose.yml`

- Web service (Flask):
  - Container: `podcast_web`
  - Port mapping: `5002:5000`
  - Command: `flask --app web.app run --host=0.0.0.0`
  - MongoDB: `mongodb://mongodb:27017/podcast_db` (internal Docker network)

## Testing Checklist

### ✅ Backend Health

- [ ] Container `podcast_web` is running: `docker ps | grep podcast_web`
- [ ] API responds: `curl http://localhost:5002/api/episodes`
- [ ] Logs are clean: `docker-compose logs podcast_web`
- [ ] MongoDB is accessible: `docker ps | grep mongodb`

### ✅ Frontend Connectivity

- [ ] Frontend loads: http://localhost:3000
- [ ] Network requests show port 5002: DevTools > Network tab
- [ ] No CORS errors: DevTools > Console tab
- [ ] API responses display: Check if dashboard loads data

### ✅ Functionality

- [ ] Dashboard page loads
- [ ] RSS Feeds page loads
- [ ] More menu page loads
- [ ] Episode detail page loads (if data exists)
- [ ] Forms submit without errors
- [ ] Notifications appear on actions

### ✅ Data Flow

- [ ] Episodes display in list
- [ ] Feed count shows correctly
- [ ] Status badges appear
- [ ] Pagination works
- [ ] Filters work (All/Completed/Processing)

## Troubleshooting

### Frontend can't reach backend

**Issue**: "Network request failed" or CORS errors

**Solutions**:
1. Verify Docker containers are running: `docker ps`
2. Check backend is accessible: `curl http://localhost:5002/api/episodes`
3. Verify frontend env var: Check `web-frontend/.env.local`
4. Restart frontend: Stop `npm run dev` and start again
5. Check Docker logs: `docker-compose logs podcast_web`

### CORS errors in console

**Issue**: `Access-Control-Allow-Origin` header missing

**Solutions**:
1. Check Flask has CORS middleware: `web/app.py` line 19
2. Verify API route has proper CORS headers
3. Restart Docker containers: `docker-compose restart podcast_web`

### Backend returns 500 error

**Issue**: API endpoint fails

**Solutions**:
1. Check backend logs: `docker-compose logs podcast_web`
2. Verify MongoDB connection: `docker ps | grep mongodb`
3. Check database data exists
4. Verify environment variables are set

### No data displaying

**Issue**: Pages load but show empty states

**Possible causes**:
1. Database is empty (normal for fresh setup)
2. Add test data:
   ```bash
   curl -X POST http://localhost:5002/api/episodes \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com/episode.mp3"}'
   ```

### Port already in use

**Issue**: "Address already in use" error

**Solutions**:
```bash
# Kill process on port 5002
lsof -ti:5002 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Restart containers
docker-compose restart
```

## Performance Notes

### Expected Load Times

- Dashboard page: < 1 second (cached)
- RSS Feeds page: < 500ms
- Episode detail: < 1 second
- API responses: 50-200ms

### Database

- MongoDB runs in Docker
- Data persists in `mongodb_data` volume
- Connection uses Docker network DNS: `mongodb://mongodb:27017`

## Debugging Tips

### View Docker Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f podcast_web

# Filter by error
docker-compose logs podcast_web | grep -i error

# Last 100 lines
docker-compose logs -f --tail=100 podcast_web
```

### Browser DevTools

1. **Network Tab**:
   - Check URLs point to `localhost:5002`
   - Verify 2xx status codes
   - Check response bodies are JSON

2. **Console Tab**:
   - Look for CORS errors
   - Check for JavaScript errors
   - Verify API errors display correctly

3. **Application Tab**:
   - Check cookies/storage
   - Verify environment is correct

### Direct API Testing

```bash
# List episodes
curl http://localhost:5002/api/episodes | jq

# Get feeds
curl http://localhost:5002/api/feeds | jq

# Get feeder status
curl http://localhost:5002/api/feeder/status | jq

# Add episode
curl -X POST http://localhost:5002/api/episodes \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/episode.mp3"}'
```

## Cleanup

### Stop containers without removing

```bash
docker-compose stop
```

### Stop and remove containers

```bash
docker-compose down
```

### Stop and remove everything including volumes

```bash
docker-compose down -v
```

### Remove specific container

```bash
docker-compose rm podcast_web
```

---

## Summary

| Component | Address | Status |
|-----------|---------|--------|
| Frontend | http://localhost:3000 | Run: `npm run dev` |
| Backend | http://localhost:5002 | Run: `docker-compose up -d` |
| Logs | http://localhost:5001 | Dozzle viewer |
| MongoDB | localhost:27017 | Docker container |

**Frontend Environment**: Points to Docker backend on port 5002  
**Backend**: Configured to use MongoDB at `mongodb://mongodb:27017` (Docker network)

---

**Status**: ✅ Ready for Testing
