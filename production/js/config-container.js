// Docker Container Configuration
// This file is loaded in Docker container environments to override default settings

// Container-specific environment variables
window.COCKPIT_CONTAINER_MODE = true;
window.COCKPIT_API_URL = window.COCKPIT_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;
window.COCKPIT_DEBUG = false; // Disable debug in production containers

// Add container class to body for CSS targeting
document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('container-mode');
});

// Container-specific console logging
console.log('🐳 Cockpit Container Mode Initialized', {
  apiUrl: window.COCKPIT_API_URL,
  host: window.location.hostname,
  protocol: window.location.protocol
});
