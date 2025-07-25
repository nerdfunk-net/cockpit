# Cockpit Offline & Container Setup

This guide explains how to run Cockpit in offline mode or Docker containers without internet access.

## 🏗️ Static Assets Structure

The application now includes a `static/` directory with all external dependencies:

```
production/
├── static/
│   ├── css/
│   │   └── fontawesome.min.css        # FontAwesome CSS (local)
│   └── webfonts/                       # FontAwesome fonts (local)
│       ├── fa-brands-400.woff2
│       ├── fa-brands-400.ttf
│       ├── fa-regular-400.woff2
│       ├── fa-regular-400.ttf
│       ├── fa-solid-900.woff2
│       ├── fa-solid-900.ttf
│       ├── fa-v4compatibility.woff2
│       └── fa-v4compatibility.ttf
├── js/
│   ├── config.js                       # Main configuration
│   ├── config-container.js             # Container-specific config
│   └── offline-manager.js              # Offline capabilities
├── service-worker.js                   # Service Worker for caching
└── container-ready.html                # Container-ready template
```

## 🔧 Configuration Files

### 1. Main Configuration (`js/config.js`)
- **Auto-detection**: Automatically detects environment (development, production, container)
- **Offline support**: Built-in caching and fallback data
- **Container awareness**: Special handling for Docker containers

### 2. Container Configuration (`js/config-container.js`)
- **Environment variables**: Sets container-specific variables
- **API URL detection**: Automatically configures backend URL
- **Container class**: Adds CSS class for container-specific styling

### 3. Offline Manager (`js/offline-manager.js`)
- **Caching**: Automatically caches API responses
- **Fallback data**: Provides default data when offline
- **Network monitoring**: Detects online/offline status changes

## 🐳 Docker Container Setup (Recommended)

### Quick Start with Static Container

The fastest way to get an offline container running is with the static Dockerfile:

```bash
# Build the offline-ready container
./build-offline-container.sh

# Or build manually
docker build -f Dockerfile.static -t cockpit-frontend:offline .

# Run the container
docker run -d --name cockpit-frontend -p 8080:80 cockpit-frontend:offline

# Test it
curl http://localhost:8080
```

### Build Script Features

The `build-offline-container.sh` script provides:
- ✅ Prerequisites validation
- ✅ Static asset verification  
- ✅ Automated Docker build with labels
- ✅ Container health testing
- ✅ Version tagging

```bash
# Basic build
./build-offline-container.sh

# Build with testing
./build-offline-container.sh --test

# Build specific version
./build-offline-container.sh --version 1.2.3
```

### Docker Compose Deployment

For production deployments with backend:

```bash
# Start the full stack
docker-compose -f docker-compose.offline.yml up -d

# Frontend only
docker-compose -f docker-compose.offline.yml up frontend

# With custom environment
cp docker-compose.override.example.yml docker-compose.override.yml
# Edit the override file with your settings
docker-compose -f docker-compose.offline.yml up -d
```

### Container Configuration Options

Environment variables for runtime configuration:

- `COCKPIT_API_URL`: Backend API endpoint (auto-detected if not set)
- `COCKPIT_CONTAINER_MODE`: Set to "true" for container mode (default: true)
- `COCKPIT_DEBUG`: Enable debug mode (default: false)

### Dockerfile Options

**Dockerfile.static** (Recommended for offline):
- ✅ No build process required
- ✅ Direct static file serving
- ✅ Smaller image size
- ✅ Faster startup
- ✅ No Node.js dependencies

**Dockerfile.frontend** (Full build):
- ⚠️ Requires build process
- ⚠️ Larger image size
- ⚠️ Longer build time
- ✅ Asset optimization
- ✅ Bundle processing
    networks:
      - cockpit-network

  cockpit-backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NAUTOBOT_HOST=https://your-nautobot.internal
      - NAUTOBOT_TOKEN=your-api-token
    networks:
      - cockpit-network

networks:
  cockpit-network:
    driver: bridge
```

### 3. Dockerfile Example

```dockerfile
# Multi-stage build for frontend (Offline-ready)
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
RUN apk add --no-cache curl

# Copy offline-ready production files
COPY --from=builder /app/production /usr/share/nginx/html

# Copy offline-optimized nginx config
COPY docker/nginx-offline.conf /etc/nginx/nginx.conf

# Copy startup script for runtime configuration
COPY docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

# Create non-root user
RUN addgroup -g 1000 -S appuser && adduser -u 1000 -S appuser -G appuser
RUN chown -R appuser:appuser /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx
RUN touch /var/run/nginx.pid && chown appuser:appuser /var/run/nginx.pid

# Environment variables for offline container
ENV COCKPIT_CONTAINER_MODE=true
ENV COCKPIT_DEBUG=false
ENV COCKPIT_API_URL=""

USER appuser
EXPOSE 80

# Health check for offline mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["/startup.sh"]
```

### 4. Build Script

Use the provided build script for easy container creation:

```bash
# Make executable and run
chmod +x build-offline-container.sh
./build-offline-container.sh
```

The build script will:
- ✅ Check all prerequisites and required files
- ✅ Verify static assets (FontAwesome, webfonts)
- ✅ Build the Docker image with proper labels
- ✅ Test container startup and health checks
- ✅ Generate a build report

## 🌐 Offline Capabilities

### Automatic Caching
- **API responses**: Automatically cached for offline use
- **Static assets**: Cached via Service Worker
- **Fallback data**: Built-in defaults when no cache available

### Cache Management
```javascript
// Check cache status
const stats = window.OfflineManager.getCacheStats();
console.log('Cache stats:', stats);

// Clear all cache
window.OfflineManager.clearCache();

// Manual caching
CockpitConfig.setCachedData('locations', locationData);
```

### Offline Detection
```javascript
// Check if offline
if (CockpitConfig.isOffline()) {
  console.log('Running in offline mode');
}

// Listen for status changes
window.addEventListener('connectionStatusChanged', (event) => {
  console.log('Connection status:', event.detail.status);
});
```

## 🛠️ Configuration Examples

### Development Mode
```javascript
// Automatic detection
// - localhost:3000 (frontend)
// - localhost:8000 (backend)
// - Debug enabled
// - Cache enabled
```

### Container Mode
```javascript
// Container detection
const CockpitConfig = {
  api: {
    baseUrl: 'http://backend:8000'  // Container service name
  },
  environment: {
    isContainer: true,
    isProduction: true
  },
  debug: {
    enabled: false  // Disabled in production
  }
};
```

### Offline Mode
```javascript
// Offline fallback data
const fallbackData = {
  locations: [{ id: 'default', name: 'Default Location' }],
  roles: [{ id: 'default', name: 'Default Role' }],
  statuses: [{ id: 'active', name: 'Active' }]
};
```

## 📱 HTML Templates

### Standard Template
- Includes offline manager
- Auto-loads container config
- Service worker registration

### Container-Ready Template (`container-ready.html`)
- Pre-configured for containers
- Shows connection status
- Cache management interface
- Offline indicator

## 🔍 Debugging

### Development Debug Info
```javascript
// Enable debug mode
window.COCKPIT_DEBUG = true;

// Check configuration
console.log('Config:', CockpitConfig);

// Check cache stats
console.log('Cache:', window.OfflineManager.getCacheStats());
```

### Container Debug
```bash
# Check environment variables
docker exec container_name env | grep COCKPIT

# Check logs
docker logs container_name

# Check nginx access
docker exec container_name cat /var/log/nginx/access.log  
```

## 🚀 Deployment Steps

### 1. Build Offline Container
```bash
# Use the build script (recommended)
./build-offline-container.sh

# Or build manually
docker build -f Dockerfile.frontend -t cockpit-frontend:offline-latest .
```

### 2. Deploy with Docker Compose
```bash
# Standard deployment
docker-compose -f docker-compose.offline.yml up -d

# Complete offline testing (with mock backend)
docker-compose -f docker-compose.offline.yml -f docker-compose.offline-override.yml --profile offline-testing up -d
```

### 3. Verify Deployment
```bash
# Check container health
docker ps
curl http://localhost/health

# Check static assets
curl http://localhost/static/css/fontawesome.min.css

# Check offline status
curl http://localhost/status
```

### 4. Production Configuration
```bash
# Set production environment variables
export COCKPIT_API_URL=http://your-backend-service:8000
export COCKPIT_CONTAINER_MODE=true
export COCKPIT_DEBUG=false

# Deploy with production settings
docker run -d \
  -p 80:80 \
  -e COCKPIT_API_URL=$COCKPIT_API_URL \
  -e COCKPIT_CONTAINER_MODE=$COCKPIT_CONTAINER_MODE \
  -e COCKPIT_DEBUG=$COCKPIT_DEBUG \
  cockpit-frontend:offline-latest
```

## 🔧 Troubleshooting

### Common Issues

1. **Fonts not loading**: Check `static/webfonts/` directory
2. **API calls failing**: Verify `COCKPIT_API_URL` environment variable
3. **Offline data missing**: Check browser localStorage and Service Worker
4. **Container detection failing**: Ensure `config-container.js` is loaded

### Debug Commands
```javascript
// Check environment
console.log('Environment:', CockpitConfig.environment);

// Check API URL
console.log('API URL:', CockpitConfig.api.baseUrl);

// Test offline fetch
window.offlineFetch('/api/nautobot/locations')
  .then(data => console.log('Data:', data));

// Check Service Worker
navigator.serviceWorker.getRegistrations()
  .then(registrations => console.log('SW:', registrations));
```

## 📋 Checklist

- [ ] Static assets downloaded to `production/static/`
- [ ] Container configuration file present
- [ ] Offline manager included in HTML
- [ ] Service worker registered
- [ ] Environment variables configured
- [ ] Cache fallback data defined
- [ ] Docker container tested offline
- [ ] Fonts loading correctly
- [ ] API calls working with fallback

---

**Ready for offline deployment! 🚀**
