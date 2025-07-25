# Cockpit Configuration Guide

## Environment Configuration

The Cockpit application uses a configuration system to handle different deployment environments. The main configuration file is located at:

```
production/js/config.js
```

## Configuration Options

### 1. API Backend Configuration

```javascript
api: {
  baseUrl: 'http://localhost:8000',  // Backend API URL
  endpoints: {
    // Authentication endpoints
    auth: {
      login: '/auth/login',
      register: '/auth/register'
    },
    // Nautobot integration endpoints
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
}
```

### 2. Environment Detection

The configuration automatically detects the environment:

- **Development**: `localhost` or `127.0.0.1`
- **Production**: Any other hostname

### 3. Debug Settings

```javascript
debug: {
  enabled: window.location.hostname === 'localhost',
  logLevel: window.location.hostname === 'localhost' ? 'debug' : 'error'
}
```

## Deployment Configurations

### Development Environment
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Debug: Enabled
- Auto-detection: Based on hostname

### Staging Environment
Update `config.js`:
```javascript
api: {
  baseUrl: 'https://staging-api.your-domain.com',
  // ... rest of configuration
}
```

### Production Environment
Update `config.js`:
```javascript
api: {
  baseUrl: 'https://api.your-domain.com',
  // ... rest of configuration
}
```

## Environment Variables Support

For more advanced deployments, you can modify `config.js` to read from environment variables:

```javascript
const CockpitConfig = {
  api: {
    baseUrl: window.ENV?.API_BASE_URL || 'http://localhost:8000',
    // ...
  }
};
```

Then inject environment variables during build:

```html
<script>
  window.ENV = {
    API_BASE_URL: '${API_BASE_URL}',
    // other variables
  };
</script>
<script src="js/config.js"></script>
```

## Usage in Code

### Getting API URLs
```javascript
// Get full API URL
const apiUrl = CockpitConfig.getApiUrl('/api/nautobot/locations');

// Use predefined endpoints
const locationsUrl = CockpitConfig.getApiUrl(CockpitConfig.api.endpoints.nautobot.locations);
```

### Environment Checks
```javascript
if (CockpitConfig.environment.isDevelopment) {
  console.log('Running in development mode');
}

if (CockpitConfig.debug.enabled) {
  console.log('Debug information');
}
```

## Benefits

1. **Environment Flexibility**: Easy deployment to different environments
2. **No Hardcoded URLs**: All URLs are configurable
3. **Auto-detection**: Automatically adapts to environment
4. **Debug Control**: Different debug levels per environment
5. **Centralized Config**: Single place to manage all settings
6. **Easy Maintenance**: Simple to update for new environments
