# Cockpit Unified Container Setup

This document describes the unified container setup that runs both the frontend and backend in a single container for improved convenience and resource efficiency.

## Overview

The unified container setup provides:
- **Single Container**: Both Node.js frontend and Python backend in one container
- **Automatic Startup**: Both services start automatically with proper sequencing
- **Development Mode**: Hot reload for both frontend and backend code
- **Production Mode**: Optimized build with static asset serving
- **Health Checks**: Monitors both services for availability

## Quick Start

### Development Mode (with hot reload)
```bash
# Using the control script
./docker-control.sh dev

# Or directly with docker-compose
docker-compose up -d
```

### Production Mode (optimized build)
```bash
# Using the control script  
./docker-control.sh prod

# Or directly with docker-compose
docker-compose -f docker-compose.production.yml up -d
```

## Container Architecture

### Development Container (`Dockerfile.unified`)
- Base: `node:18-alpine` with Python 3 installed
- Frontend: Vite dev server with hot reload (`npm run dev`)
- Backend: FastAPI server with auto-reload (`python start.py`)
- Volumes: Source code mounted for hot reload
- Database: Persistent SQLite database in `./data/settings/`

### Production Container (`Dockerfile.unified.production`)
- Base: `node:18-alpine` with Python 3 installed  
- Frontend: Pre-built assets served by Vite preview server (`npm run preview`)
- Backend: FastAPI server in production mode
- No source volumes: Everything built into the image
- Database: Persistent SQLite database in `./data/settings/`

## Persistent Data

### Database Storage
The SQLite database containing all settings is now stored persistently outside the container:

- **Host Path**: `./data/settings/cockpit_settings.db`
- **Container Path**: `/app/backend/settings/cockpit_settings.db`
- **Benefits**: Settings survive container restarts and updates

### Data Directory Structure
```
data/
└── settings/
    └── cockpit_settings.db    # SQLite database with Nautobot and Git settings
```

### Backup and Restore
```bash
# Backup database
cp ./data/settings/cockpit_settings.db ./backups/cockpit_settings_$(date +%Y%m%d).db

# Restore database
cp ./backups/cockpit_settings_20240101.db ./data/settings/cockpit_settings.db
docker-compose restart
```

## Service Startup Sequence

1. **Backend starts first** in background mode
2. **2-second delay** to ensure backend is ready
3. **Frontend starts** in foreground mode (keeps container alive)

Both services are monitored by Docker health checks.

## Ports

- **3000**: Frontend (Vite dev server or preview server)
- **8000**: Backend (FastAPI server)

## Environment Variables

All environment variables from the original setup are supported:

### Frontend Configuration
- `NODE_ENV`: development/production
- `VITE_HOST`: Vite server host (default: 0.0.0.0)  
- `VITE_PORT`: Vite server port (default: 3000)

### Backend Configuration
- `SERVER_HOST`: FastAPI server host (default: 0.0.0.0)
- `SERVER_PORT`: FastAPI server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)

### Nautobot Configuration
- `NAUTOBOT_HOST`: Nautobot server URL
- `NAUTOBOT_TOKEN`: Nautobot API token
- `NAUTOBOT_TIMEOUT`: Request timeout (default: 30)

### Authentication Configuration  
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiry (default: 30)

### CORS Configuration
- `CORS_ORIGINS`: Allowed origins (default: http://localhost:3000)
- `CORS_ALLOW_CREDENTIALS`: Allow credentials (default: true)

## Management Commands

### Using the Control Script

```bash
# Start development container
./docker-control.sh dev

# Start production container  
./docker-control.sh prod

# Stop all containers
./docker-control.sh stop

# Restart containers
./docker-control.sh restart

# View logs
./docker-control.sh logs

# Rebuild containers
./docker-control.sh build

# Clean up everything
./docker-control.sh clean
```

### Direct Docker Commands

```bash
# Development
docker-compose up -d
docker-compose logs -f
docker-compose down

# Production
docker-compose -f docker-compose.production.yml up -d
docker-compose -f docker-compose.production.yml logs -f  
docker-compose -f docker-compose.production.yml down

# Build
docker-compose build --no-cache
```

## Health Checks

The container includes health checks that verify both services:

```bash
# Check status
docker-compose ps

# Manual health check
docker exec cockpit-unified curl -f http://localhost:3000/
docker exec cockpit-unified curl -f http://localhost:8000/docs
```

## Troubleshooting

### Container Won't Start
1. Check Docker logs: `docker-compose logs`
2. Verify environment variables are set
3. Ensure Nautobot network exists: `docker network ls`

### Frontend Not Loading
1. Check if port 3000 is accessible
2. Verify CORS settings in environment variables
3. Check frontend logs in container output

### Backend API Errors
1. Check if port 8000 is accessible  
2. Verify Nautobot configuration
3. Check backend logs in container output

### Development Hot Reload Not Working
1. Ensure source code is mounted as volumes
2. Check file permissions on mounted volumes
3. Restart container if needed

## Migration from Dual Container Setup

To migrate from the old two-container setup:

1. **Stop old containers**:
   ```bash
   docker-compose down
   ```

2. **Update your docker-compose.yml** (already done)

3. **Start unified container**:
   ```bash
   ./docker-control.sh dev
   ```

4. **Verify both services**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000/docs

## Benefits of Unified Container

- **Simplified Deployment**: One container instead of two
- **Automatic Service Coordination**: Backend always starts before frontend
- **Resource Efficiency**: Shared base image and reduced overhead
- **Easier Logging**: All logs in one place
- **Simplified Networking**: No inter-container communication needed

## Files Created

- `Dockerfile.unified` - Development container
- `Dockerfile.unified.production` - Production container  
- `start-unified.sh` - Development startup script
- `start-unified-production.sh` - Production startup script
- `docker-compose.yml` - Updated for unified container
- `docker-compose.production.yml` - Production configuration
- `docker-control.sh` - Management script
- `DOCKER_UNIFIED_README.md` - This documentation
