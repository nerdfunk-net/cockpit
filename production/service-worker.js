// Service Worker for Cockpit Offline Capability
// Caches static assets and API responses for offline use

const CACHE_NAME = 'cockpit-offline-v1';
const STATIC_CACHE_NAME = 'cockpit-static-v1';

// Files to cache for offline use
const STATIC_FILES = [
  '/',
  '/index.html',
  '/login.html',
  '/onboard-device.html',
  '/static/css/fontawesome.min.css',
  '/static/webfonts/fa-brands-400.woff2',
  '/static/webfonts/fa-regular-400.woff2',
  '/static/webfonts/fa-solid-900.woff2',
  '/js/config.js',
  '/js/config-container.js',
  '/js/offline-manager.js',
  '/js/auth.js',
  '/images/favicon.ico'
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/nautobot/locations',
  '/api/nautobot/roles',
  '/api/nautobot/statuses',
  '/api/nautobot/platforms',
  '/api/nautobot/namespaces',
  '/api/nautobot/secret-groups'
];

// Install event - cache static files
self.addEventListener('install', event => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('📦 Caching static files');
        return cache.addAll(STATIC_FILES.map(url => new Request(url, { cache: 'reload' })));
      })
      .then(() => {
        console.log('✅ Static files cached');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('❌ Failed to cache static files:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('🚀 Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME && cacheName !== STATIC_CACHE_NAME) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle static file requests
  if (STATIC_FILES.some(file => url.pathname === file || url.pathname.endsWith(file))) {
    event.respondWith(handleStaticRequest(request));
    return;
  }

  // Handle other requests with network-first strategy
  event.respondWith(
    fetch(request)
      .catch(() => {
        // If network fails, try cache
        return caches.match(request);
      })
  );
});

// Handle API requests with cache fallback
async function handleApiRequest(request) {
  const cache = await caches.open(CACHE_NAME);
  
  try {
    // Try network first
    const response = await fetch(request);
    
    if (response.ok && request.method === 'GET') {
      // Cache successful GET requests
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.warn('🌐 API request failed, trying cache:', request.url);
    
    // Network failed, try cache
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      console.log('📦 Serving API response from cache:', request.url);
      return cachedResponse;
    }
    
    // No cache available, return error response
    return new Response(
      JSON.stringify({ 
        error: 'Offline - No cached data available',
        offline: true 
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle static file requests with cache-first strategy
async function handleStaticRequest(request) {
  const cache = await caches.open(STATIC_CACHE_NAME);
  
  // Try cache first
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    console.log('📦 Serving static file from cache:', request.url);
    return cachedResponse;
  }
  
  try {
    // Cache miss, try network
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('❌ Failed to fetch static file:', request.url, error);
    
    // Return a fallback response for critical files
    if (request.url.includes('.html')) {
      return new Response(
        '<!DOCTYPE html><html><head><title>Offline</title></head><body><h1>Offline Mode</h1><p>This page is not available offline.</p></body></html>',
        { headers: { 'Content-Type': 'text/html' } }
      );
    }
    
    throw error;
  }
}

// Handle messages from main thread
self.addEventListener('message', event => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'CACHE_API_RESPONSE':
      cacheApiResponse(data.url, data.response);
      break;
    case 'CLEAR_CACHE':
      clearAllCaches();
      break;
    case 'GET_CACHE_STATUS':
      getCacheStatus().then(status => {
        event.ports[0].postMessage(status);
      });
      break;
  }
});

// Cache an API response manually
async function cacheApiResponse(url, responseData) {
  const cache = await caches.open(CACHE_NAME);
  const response = new Response(JSON.stringify(responseData), {
    headers: { 'Content-Type': 'application/json' }
  });
  await cache.put(url, response);
  console.log('📦 Manually cached API response:', url);
}

// Clear all caches
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(cacheNames.map(name => caches.delete(name)));
  console.log('🗑️ All caches cleared');
}

// Get cache status
async function getCacheStatus() {
  const staticCache = await caches.open(STATIC_CACHE_NAME);
  const apiCache = await caches.open(CACHE_NAME);
  
  const staticKeys = await staticCache.keys();
  const apiKeys = await apiCache.keys();
  
  return {
    staticFiles: staticKeys.length,
    apiResponses: apiKeys.length,
    totalCached: staticKeys.length + apiKeys.length
  };
}
