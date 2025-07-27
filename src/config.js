/**
 * Frontend Configuration
 * This file contains all configurable parameters for the Cockpit frontend.
 * Modify these values according to your environment.
 */

// API Configuration
export const API_CONFIG = {
  // Backend API base URL
  BASE_URL: window.location.protocol === 'https:' 
    ? 'https://localhost:8000' 
    : 'http://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    DEVICES: '/api/nautobot/devices',
    AUTH_LOGIN: '/auth/login',
    AUTH_VERIFY: '/auth/verify',
    NAMESPACES: '/api/nautobot/namespaces',
    SYNC_NETWORK: '/api/nautobot/sync-network-data'
  },
  
  // Request timeout in milliseconds
  TIMEOUT: 30000,
  
  // Retry configuration
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
};

// UI Configuration
export const UI_CONFIG = {
  // Pagination
  PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  
  // Table configuration
  TABLE_CONFIG: {
    SEARCH_DEBOUNCE: 500,
    SORT_DIRECTION: 'asc'
  },
  
  // Filter configuration
  FILTERS: {
    NAME_MIN_LENGTH: 3,
    LOCATION_MIN_LENGTH: 3,
    REGEX_TIMEOUT: 5000
  },
  
  // Theme configuration
  THEME: {
    DEFAULT_THEME: 'light',
    AVAILABLE_THEMES: ['light', 'dark']
  }
};

// Development Configuration
export const DEV_CONFIG = {
  // Enable debug logging
  DEBUG: false,
  
  // Mock data for development
  USE_MOCK_DATA: false,
  
  // Enable performance monitoring
  PERFORMANCE_MONITORING: false
};

// Security Configuration
export const SECURITY_CONFIG = {
  // Token storage key
  TOKEN_STORAGE_KEY: 'auth_token',
  
  // Token refresh buffer (in milliseconds)
  TOKEN_REFRESH_BUFFER: 300000, // 5 minutes
  
  // Session timeout (in milliseconds)
  SESSION_TIMEOUT: 3600000 // 1 hour
};

// Export combined configuration
export const CONFIG = {
  API: API_CONFIG,
  UI: UI_CONFIG,
  DEV: DEV_CONFIG,
  SECURITY: SECURITY_CONFIG
};
