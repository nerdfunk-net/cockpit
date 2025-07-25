// Configuration for Cockpit application
// This file contains environment-specific settings

const CockpitConfig = {
  // API Backend Configuration
  api: {
    // In offline/container mode, detect backend from current host or use environment variable
    baseUrl: (() => {
      // Check for environment variable first (Docker containers)
      if (typeof window !== 'undefined' && window.COCKPIT_API_URL) {
        return window.COCKPIT_API_URL;
      }
      
      // Auto-detect for offline/container deployments
      const protocol = window.location.protocol;
      const hostname = window.location.hostname;
      
      // For container deployments, backend typically runs on same host, different port
      if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        // Production/container mode - backend on same host, port 8000
        return `${protocol}//${hostname}:8000`;
      }
      
      // Development mode
      return protocol === 'https:' 
        ? 'https://localhost:8000'  // Use HTTPS in production
        : 'http://localhost:8000';  // Use HTTP in development
    })(),
    
    // Alternative: detect from current host
    // baseUrl: `${window.location.protocol}//${window.location.hostname}:8000`,
    
    endpoints: {
      auth: {
        login: '/auth/login',
        register: '/auth/register'
      },
      nautobot: {
        locations: '/api/nautobot/locations',
        namespaces: '/api/nautobot/namespaces',
        roles: '/api/nautobot/roles',
        platforms: '/api/nautobot/platforms',
        statuses: '/api/nautobot/statuses',
        secretGroups: '/api/nautobot/secret-groups',
        checkIp: '/api/nautobot/check-ip',
        onboardDevice: '/api/nautobot/devices/onboard'
      }
    }
  },

  // Frontend Configuration
  frontend: {
    // Auto-detect frontend URL
    baseUrl: `${window.location.protocol}//${window.location.host}`
  },

  // Environment Detection
  environment: {
    isDevelopment: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
    isProduction: window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1',
    isContainer: typeof window !== 'undefined' && (window.COCKPIT_CONTAINER_MODE === true || document.body.classList.contains('container-mode')),
    isOffline: !navigator.onLine
  },

  // Offline Configuration
  offline: {
    // Enable offline mode features
    enabled: true,
    // Cache key for localStorage
    cacheKey: 'cockpit_offline_cache',
    // Maximum cache age in milliseconds (24 hours)
    maxCacheAge: 24 * 60 * 60 * 1000,
    // Fallback data when offline
    fallbackData: {
      locations: [{ id: 'default', name: 'Default Location' }],
      roles: [{ id: 'default', name: 'Default Role' }],
      statuses: [{ id: 'active', name: 'Active' }],
      platforms: [{ id: 'default', name: 'Default Platform' }],
      namespaces: [{ id: 'default', name: 'Default Namespace' }],
      secretGroups: [{ id: 'default', name: 'Default Secret Group' }]
    }
  },

  // Debug Settings
  debug: {
    enabled: window.location.hostname === 'localhost' || (window.COCKPIT_DEBUG === true),
    logLevel: window.location.hostname === 'localhost' ? 'debug' : 'error',
    showOfflineStatus: true,
    showContainerInfo: true
  }
};

// Helper function to get full API URL
CockpitConfig.getApiUrl = function(endpoint) {
  return this.api.baseUrl + endpoint;
};

// Helper function to get full frontend URL
CockpitConfig.getFrontendUrl = function(path = '') {
  return this.frontend.baseUrl + path;
};

// Helper function to check if offline
CockpitConfig.isOffline = function() {
  return !navigator.onLine || this.environment.isOffline;
};

// Helper function to get cached data
CockpitConfig.getCachedData = function(key) {
  if (!this.offline.enabled) return null;
  
  try {
    const cached = localStorage.getItem(`${this.offline.cacheKey}_${key}`);
    if (!cached) return null;
    
    const data = JSON.parse(cached);
    const age = Date.now() - data.timestamp;
    
    if (age > this.offline.maxCacheAge) {
      localStorage.removeItem(`${this.offline.cacheKey}_${key}`);
      return null;
    }
    
    return data.value;
  } catch (error) {
    console.warn('Error reading cached data:', error);
    return null;
  }
};

// Helper function to cache data
CockpitConfig.setCachedData = function(key, value) {
  if (!this.offline.enabled) return;
  
  try {
    const data = {
      value: value,
      timestamp: Date.now()
    };
    localStorage.setItem(`${this.offline.cacheKey}_${key}`, JSON.stringify(data));
  } catch (error) {
    console.warn('Error caching data:', error);
  }
};

// Helper function to get fallback data when offline
CockpitConfig.getFallbackData = function(key) {
  // First try cache
  const cached = this.getCachedData(key);
  if (cached) return cached;
  
  // Then try fallback data
  if (this.offline.fallbackData[key]) {
    return this.offline.fallbackData[key];
  }
  
  // Return empty array as last resort
  return [];
};

// Enhanced API call helper with offline support
CockpitConfig.apiCall = async function(endpoint, options = {}) {
  const url = this.getApiUrl(endpoint);
  const cacheKey = `api_${endpoint.replace(/[^a-zA-Z0-9]/g, '_')}`;
  
  // If offline, return cached or fallback data
  if (this.isOffline()) {
    console.warn('Offline mode: returning cached/fallback data for', endpoint);
    const fallbackKey = endpoint.split('/').pop(); // Extract key from endpoint
    return this.getFallbackData(fallbackKey);
  }
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Cache successful responses
    if (response.status === 200 && (options.method === 'GET' || !options.method)) {
      const fallbackKey = endpoint.split('/').pop();
      this.setCachedData(fallbackKey, data);
    }
    
    return data;
  } catch (error) {
    console.warn('API call failed, trying cached data:', error);
    
    // Try to return cached data on error
    const fallbackKey = endpoint.split('/').pop();
    const fallbackData = this.getFallbackData(fallbackKey);
    
    if (fallbackData.length > 0) {
      return fallbackData;
    }
    
    throw error;
  }
};

// Make config globally available
window.CockpitConfig = CockpitConfig;

// Initialize offline status monitoring
if (CockpitConfig.offline.enabled) {
  // Monitor online/offline status
  window.addEventListener('online', () => {
    CockpitConfig.environment.isOffline = false;
    if (CockpitConfig.debug.showOfflineStatus) {
      console.log('🟢 Connection restored - Online mode');
    }
  });
  
  window.addEventListener('offline', () => {
    CockpitConfig.environment.isOffline = true;
    if (CockpitConfig.debug.showOfflineStatus) {
      console.warn('🔴 Connection lost - Offline mode activated');
    }
  });
}

// Log configuration in development or when debug is enabled
if (CockpitConfig.debug.enabled) {
  console.log('🚀 Cockpit Configuration Loaded:', {
    environment: CockpitConfig.environment,
    apiBaseUrl: CockpitConfig.api.baseUrl,
    offlineEnabled: CockpitConfig.offline.enabled,
    isOnline: navigator.onLine
  });
  
  if (CockpitConfig.debug.showContainerInfo && CockpitConfig.environment.isContainer) {
    console.log('🐳 Container mode detected');
  }
  
  if (CockpitConfig.debug.showOfflineStatus && !navigator.onLine) {
    console.warn('⚠️ Starting in offline mode');
  }
}
