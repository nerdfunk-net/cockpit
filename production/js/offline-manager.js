// Offline Utilities for Cockpit
// Provides offline capability and caching for API calls

class OfflineManager {
  constructor(config = window.CockpitConfig) {
    this.config = config;
    this.isInitialized = false;
    this.init();
  }

  init() {
    if (this.isInitialized) return;

    // Set up service worker for caching (if available)
    if ('serviceWorker' in navigator) {
      this.registerServiceWorker();
    }

    // Monitor network status
    this.setupNetworkMonitoring();
    
    this.isInitialized = true;
    console.log('🔧 OfflineManager initialized');
  }

  async registerServiceWorker() {
    try {
      const registration = await navigator.serviceWorker.register('/service-worker.js');
      console.log('📦 Service Worker registered:', registration);
    } catch (error) {
      console.warn('⚠️ Service Worker registration failed:', error);
    }
  }

  setupNetworkMonitoring() {
    // Update connection status
    const updateStatus = () => {
      const wasOffline = this.config.environment.isOffline;
      this.config.environment.isOffline = !navigator.onLine;
      
      if (wasOffline !== this.config.environment.isOffline) {
        this.notifyStatusChange();
      }
    };

    window.addEventListener('online', updateStatus);
    window.addEventListener('offline', updateStatus);
    
    // Initial status check
    updateStatus();
  }

  notifyStatusChange() {
    const status = this.config.environment.isOffline ? 'offline' : 'online';
    const event = new CustomEvent('connectionStatusChanged', { 
      detail: { 
        isOffline: this.config.environment.isOffline,
        status: status
      } 
    });
    window.dispatchEvent(event);
    
    if (this.config.debug.showOfflineStatus) {
      console.log(`🔄 Connection status changed: ${status}`);
    }
  }

  // Enhanced fetch with offline fallback
  async fetch(endpoint, options = {}) {
    const url = typeof endpoint === 'string' ? this.config.getApiUrl(endpoint) : endpoint;
    const cacheKey = this.getCacheKey(url, options);

    // If offline, return cached data immediately
    if (this.config.isOffline()) {
      const cached = this.config.getCachedData(cacheKey);
      if (cached) {
        console.log('📦 Returning cached data for:', url);
        return { ok: true, json: () => Promise.resolve(cached) };
      }

      // No cache available, return fallback
      const fallbackData = this.getFallbackForEndpoint(endpoint);
      if (fallbackData) {
        console.log('🔄 Returning fallback data for:', url);
        return { ok: true, json: () => Promise.resolve(fallbackData) };
      }

      throw new Error('No cached data available for offline use');
    }

    try {
      // Online - make actual request
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      // Cache successful GET requests
      if (response.ok && (!options.method || options.method === 'GET')) {
        const data = await response.clone().json();
        this.config.setCachedData(cacheKey, data);
      }

      return response;
    } catch (error) {
      console.warn('🌐 Network request failed, trying cache:', error);
      
      // Network error - try cache
      const cached = this.config.getCachedData(cacheKey);
      if (cached) {
        return { ok: true, json: () => Promise.resolve(cached) };
      }

      // No cache - try fallback
      const fallbackData = this.getFallbackForEndpoint(endpoint);
      if (fallbackData) {
        return { ok: true, json: () => Promise.resolve(fallbackData) };
      }

      throw error;
    }
  }

  getCacheKey(url, options) {
    const method = options.method || 'GET';
    const body = options.body ? JSON.stringify(options.body) : '';
    return `${method}_${url}_${body}`.replace(/[^a-zA-Z0-9]/g, '_');
  }

  getFallbackForEndpoint(endpoint) {
    // Extract the data type from endpoint
    const endpointMap = {
      '/api/nautobot/locations': 'locations',
      '/api/nautobot/roles': 'roles',
      '/api/nautobot/statuses': 'statuses',
      '/api/nautobot/platforms': 'platforms',
      '/api/nautobot/namespaces': 'namespaces',
      '/api/nautobot/secret-groups': 'secretGroups'
    };

    const dataType = endpointMap[endpoint];
    if (dataType && this.config.offline.fallbackData[dataType]) {
      return this.config.offline.fallbackData[dataType];
    }

    return null;
  }

  // Clear all cached data
  clearCache() {
    const keys = Object.keys(localStorage);
    const cacheKeys = keys.filter(key => key.startsWith(this.config.offline.cacheKey));
    
    cacheKeys.forEach(key => localStorage.removeItem(key));
    console.log(`🗑️ Cleared ${cacheKeys.length} cached items`);
  }

  // Get cache statistics
  getCacheStats() {
    const keys = Object.keys(localStorage);
    const cacheKeys = keys.filter(key => key.startsWith(this.config.offline.cacheKey));
    
    let totalSize = 0;
    const items = cacheKeys.map(key => {
      const value = localStorage.getItem(key);
      const size = value ? value.length : 0;
      totalSize += size;
      
      try {
        const data = JSON.parse(value);
        return {
          key: key.replace(this.config.offline.cacheKey + '_', ''),
          size: size,
          age: Date.now() - data.timestamp,
          isExpired: (Date.now() - data.timestamp) > this.config.offline.maxCacheAge
        };
      } catch {
        return { key, size, age: 0, isExpired: false };
      }
    });

    return {
      totalItems: cacheKeys.length,
      totalSize: totalSize,
      items: items
    };
  }
}

// Create global instance
window.OfflineManager = new OfflineManager();

// Enhanced fetch function for components to use
window.offlineFetch = (endpoint, options) => {
  return window.OfflineManager.fetch(endpoint, options);
};

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = OfflineManager;
}
