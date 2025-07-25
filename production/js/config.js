// Configuration for Cockpit application
// This file contains environment-specific settings

const CockpitConfig = {
  // API Backend Configuration
  api: {
    baseUrl: window.location.protocol === 'https:' 
      ? 'https://localhost:8000'  // Use HTTPS in production
      : 'http://localhost:8000',  // Use HTTP in development
    
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
    isProduction: window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
  },

  // Debug Settings
  debug: {
    enabled: window.location.hostname === 'localhost',
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

// Make config globally available
window.CockpitConfig = CockpitConfig;

// Log configuration in development
if (CockpitConfig.debug.enabled) {
  console.log('Cockpit Configuration:', CockpitConfig);
}
