// Configuration for Cockpit application
// This file contains environment-specific settings

const CockpitConfig = {
  // API Backend Configuration
  api: {
    // Auto-detect backend URL based on current environment
    baseUrl: (() => {
      // Check for environment variable first (Docker containers)
      if (typeof window !== 'undefined' && window.COCKPIT_API_URL) {
        return window.COCKPIT_API_URL;
      }
      
      // Auto-detect for container deployments
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
        deviceRoles: '/api/nautobot/roles/devices',
        platforms: '/api/nautobot/platforms',
        statuses: '/api/nautobot/statuses',
        deviceStatuses: '/api/nautobot/statuses/device',
        interfaceStatuses: '/api/nautobot/statuses/interface',
        ipAddressStatuses: '/api/nautobot/statuses/ipaddress',
        combinedStatuses: '/api/nautobot/statuses/combined',
        secretGroups: '/api/nautobot/secret-groups',
        stats: '/api/nautobot/stats',
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
    isContainer: typeof window !== 'undefined' && (window.COCKPIT_CONTAINER_MODE === true || (document.body && document.body.classList.contains('container-mode')))
  },

  // Debug Settings
  debug: {
    enabled: window.location.hostname === 'localhost' || (window.COCKPIT_DEBUG === true),
    logLevel: window.location.hostname === 'localhost' ? 'debug' : 'error'
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

// Simple API call helper
CockpitConfig.apiCall = async function(endpoint, options = {}) {
  const url = this.getApiUrl(endpoint);
  
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
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// Make config globally available
window.CockpitConfig = CockpitConfig;

// Log configuration in development or when debug is enabled
if (CockpitConfig.debug.enabled) {
  console.log('🚀 Cockpit Configuration Loaded:', {
    environment: CockpitConfig.environment,
    apiBaseUrl: CockpitConfig.api.baseUrl
  });
  
  if (CockpitConfig.debug.showContainerInfo && CockpitConfig.environment.isContainer) {
    console.log('🐳 Container mode detected');
  }
}
