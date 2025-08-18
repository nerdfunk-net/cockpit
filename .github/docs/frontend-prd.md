# Cockpit Frontend PRD

## Table of Contents

1. [Frontend Overview](#1-frontend-overview)
2. [Technology Stack](#2-technology-stack)
3. [UI Architecture](#3-ui-architecture)  
4. [Build System](#4-build-system)
5. [Authentication Integration](#5-authentication-integration)
6. [API Communication](#6-api-communication)
7. [Component Library](#7-component-library)
8. [Page Structure](#8-page-structure)
9. [Configuration Management](#9-configuration-management)
10. [Development Workflow](#10-development-workflow)
11. [Deployment](#11-deployment)
12. [Known Limitations](#12-known-limitations)

## 1. Frontend Overview

**Cockpit Frontend** is a modern web dashboard built with Vite and Bootstrap 5, providing a network management interface for network engineers and NetDevOps teams.

**Core Purpose:**
- Responsive Bootstrap 5 UI based on Gentelella template
- Multi-page application with Vite build system
- JWT-based authentication with session management
- Real-time API communication with backend services

**Target Users:**
- Network Engineers
- Site Reliability Engineers (SREs)
- NetDevOps Teams
- Infrastructure Automation Engineers

## 2. Technology Stack

### Core Framework
- **Build Tool:** Vite 6.3.5+ with ES2022 target
- **UI Framework:** Bootstrap 5 with Gentelella template
- **Language:** JavaScript ES6+ (no TypeScript)
- **Styling:** SCSS with main entry at `src/main.scss`

### Legacy Support
- **jQuery:** Required for existing widgets and UI components
- **jQuery UI:** For enhanced interactions and effects

### Dependencies (37 total)
```json
{
  "dependencies": {
    // Core Framework
    "bootstrap": "^5.3.0",
    "@popperjs/core": "^2.11.8", 
    "jquery": "^3.7.1",
    
    // UI Components
    "select2": "^4.1.0",
    "switchery": "^0.8.2",
    "datatables.net": "^2.1.8",
    "jquery-ui": "^1.14.0",
    
    // Charts & Visualization
    "chart.js": "^4.4.4",
    "echarts": "^5.5.1",
    "leaflet": "^1.9.4",
    
    // Forms & Inputs
    "ion-rangeslider": "^2.3.1",
    "autosize": "^6.0.1",
    "@eonasdan/tempus-dominus": "^6.9.7",
    
    // Utilities
    "dayjs": "^1.11.13",
    "nprogress": "^0.2.0",
    "jquery-sparkline": "^2.4.0"
  }
}
```

### Development Environment
- **Frontend Dev Server:** Vite on port 3000/3001 with proxy to backend
- **Hot Reload:** File watching with auto-refresh
- **Proxy Configuration:** `/api` and `/auth` routes proxied to backend:8000

## 3. UI Architecture

### Layout System
Cockpit uses the **Gentelella Bootstrap 5** template with a consistent three-panel layout:

#### Left Sidebar Navigation (230px width)
- **Brand Header:** "Cockpit!" logo with paw icon  
- **User Profile Section:** Welcome message with username display
- **Hierarchical Menu Structure:** Collapsible menu sections with FontAwesome icons
- **Menu Footer:** Quick action buttons (Settings, Visibility toggle, Logout)
- **Responsive Behavior:** Collapses to 70px on smaller screens with icon-only view

#### Top Navigation Bar
- **Hamburger Menu Toggle:** Controls sidebar collapse/expand
- **User Dropdown:** Profile access and logout option
- **Breadcrumb Context:** Page-specific information

#### Main Content Area (Right Panel)
- **Page Title Section:** Heading with optional action buttons
- **Content Panels:** Bootstrap card-based layout with collapsible sections
- **Footer:** Fixed positioning with proper margin spacing

### Navigation Menu Structure
```
General
├── 🏠 Home (index.html)
├── 🚀 Onboarding
│   ├── ➕ Onboard Device (onboard-device.html)
│   ├── 🔄 Sync Devices (sync_devices.html)
│   └── 🔍 Scan & Add (scan-and-add.html)
├── ⚙️ Configs
│   ├── 💾 Backup (backup.html)
│   └── 🔄 Compare (compare.html)
├── ⚙️ Ansible
│   └── 📋 Inventory (ansible-inventory.html)
└── 🔧 Settings
    ├── 🖥️ Nautobot (settings-nautobot.html)
    ├── 📝 Templates (settings-templates.html)
    ├── 🔀 Git Management (settings-git.html)
    ├── ⚡ Cache (settings-cache.html)
    └── 🔑 Credentials (settings-credentials.html)
```

## 4. Build System

### Vite Configuration (`vite.config.js`)
```javascript
export default defineConfig({
  root: ".",
  publicDir: "production",
  
  build: {
    outDir: "dist",
    emptyOutDir: true,
    target: "es2022",
    rollupOptions: {
      output: {
        manualChunks: {
          "vendor-core": ["jquery", "bootstrap", "@popperjs/core"],
          "vendor-charts": ["chart.js", "echarts", "leaflet"],
          "vendor-forms": ["select2", "ion-rangeslider", "autosize", "switchery"],
          "vendor-ui": ["jquery-ui", "nprogress", "datatables.net"],
          "vendor-utils": ["dayjs", "jquery-sparkline", "skycons"]
        }
      },
      input: {
        // Multi-page application entries
        main: "production/index.html",
        login: "production/login.html",
        
        // Cockpit Applications
        compare: "production/compare.html", 
        onboard_device: "production/onboard-device.html",
        scan_and_add: "production/scan-and-add.html",
        ansible_inventory: "production/ansible-inventory.html",
        sync_devices: "production/sync_devices.html",
        backup: "production/backup.html",
        
        // Settings Applications
        settings: "production/settings.html",
        settings_nautobot: "production/settings-nautobot.html",
        settings_templates: "production/settings-templates.html", 
        settings_git: "production/settings-git.html",
        settings_cache: "production/settings-cache.html",
        settings_credentials: "production/settings-credentials.html"
      }
    }
  },
  
  server: {
    port: 3000,
    host: process.env.VITE_HOST || "localhost",
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false
      },
      "/auth": {
        target: "http://127.0.0.1:8000", 
        changeOrigin: true,
        secure: false
      }
    }
  }
});
```

### SCSS Build Pipeline
```scss
// Main SCSS entry point (src/main.scss)
@import "scss/bootstrap-custom";
@import "scss/components";
@import "scss/forms";
@import "scss/charts";
@import "scss/vendor-overrides";
```

### Bundle Optimization
- **Tree Shaking:** Automatic dead code elimination
- **Code Splitting:** Vendor chunks separated by functionality
- **Asset Management:** Images, fonts, and static assets with hashing
- **Terser Minification:** Production builds with console.log removal

## 5. Authentication Integration

### AuthManager Class (`production/js/auth.js`)
```javascript
class AuthManager {
  constructor() {
    this.token = localStorage.getItem('auth_token');
    this.userInfo = this.getUserInfo();
    this.baseURL = this.getBaseUrl();
    this.isDevelopment = this.detectDevelopment();
  }
  
  async login(username, password) {
    const loginUrl = this.isDevelopment ? '/auth/login' : `${this.baseURL}/auth/login`;
    // JWT token handling
  }
  
  async apiRequest(endpoint, options = {}) {
    // Automatic authentication header injection
    // Development vs production URL handling
    // Token refresh on 401 responses
  }
  
  requireAuth() {
    // Page protection with redirect to login
  }
}
```

### Session Management
- **Token Storage:** localStorage for JWT tokens
- **Cross-Tab Sync:** Storage event listeners for session synchronization
- **Auto-Refresh:** Token refresh mechanism before expiry
- **Development Detection:** Automatic environment detection for URL construction

### Page Protection Pattern
```html
<script>
  // Robust authentication check on every protected page
  (function () {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      window.location.href = "/login.html";
      return;
    }
  })();
</script>
```

## 6. API Communication

### Development vs Production URL Strategy
```javascript
// Auto-detection pattern used throughout frontend
const isDevelopment = window.location.port === "3000" || window.location.port === "3001";

if (isDevelopment) {
  // Use relative URLs for Vite proxy
  baseUrl = "";
} else {
  // Use absolute URLs for production
  baseUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
}
```

### Configuration Management (`production/js/config.js`)
```javascript
const CockpitConfig = {
  api: {
    baseUrl: (() => {
      // Complex auto-detection logic
      // Environment variable overrides
      // Vite environment detection
      // Container mode handling
    })(),
    
    endpoints: {
      auth: {
        login: "/auth/login",
        refresh: "/auth/refresh"
      },
      nautobot: {
        locations: "/api/nautobot/locations",
        devices: "/api/nautobot/devices",
        onboardDevice: "/api/nautobot/devices/onboard"
      },
      settings: {
        nautobot: "/api/settings/nautobot",
        git: "/api/settings/git",
        cache: "/api/settings/cache"
      },
      templates: {
        list: "/api/templates",
        create: "/api/templates",
        render: "/api/templates/render",
        import: "/api/templates/import"
      },
      git: {
        status: "/api/git/status",
        sync: "/api/git/sync",
        repositories: "/api/git/repositories"
      }
    }
  }
};
```

### Container Configuration Override
```javascript
// Container-specific configuration (production/js/config-container.js)
// Loaded only in non-localhost environments
// Handles Docker container URL overrides
// Prevents interference with Vite development proxy
```

## 7. Component Library

### Form Components
- **Select2:** Enhanced dropdowns with search and tagging
- **Switchery:** iOS-style toggle switches
- **Ion Range Slider:** Range inputs with dual handles
- **Tempus Dominus:** Date/time picker components
- **Autosize:** Auto-expanding textareas

### Settings-Specific Components
- **Template Editor:** Code editor with syntax highlighting
- **Repository Connection Tester:** Live connection validation
- **Cache Statistics Display:** Real-time performance metrics
- **SSL Certificate Validator:** Certificate chain verification
- **Template Variable Extractor:** Automatic Jinja2 variable detection
- **Git Repository Browser:** File tree navigation and selection

### Data Tables
- **DataTables:** Sortable, searchable, paginated tables
- **Responsive Design:** Mobile-friendly table layouts
- **Action Buttons:** Inline edit, delete, view actions

### Charts & Visualization  
- **Chart.js:** Line, bar, pie, and doughnut charts
- **ECharts:** Advanced charting with animations
- **Leaflet:** Interactive maps for geographic data
- **jQuery Sparkline:** Inline mini-charts

### UI Enhancements
- **NProgress:** Page loading progress bars
- **jQuery UI:** Drag & drop, sortable, resizable
- **FontAwesome:** Comprehensive icon library
- **Bootstrap Components:** Cards, modals, tooltips, popovers

## 8. Page Structure

### Multi-Page Application Architecture
Each page follows a consistent structure:

```html
<!doctype html>
<html lang="en">
<head>
  <!-- Standard meta tags -->
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Page Title - Cockpit</title>

  <!-- Vite Entry Point -->
  <script type="module" src="/src/main-minimal.js"></script>
  
  <!-- Configuration -->
  <script src="js/config.js"></script>
  
  <!-- Container Configuration (Production) -->
  <script>
    const currentPort = window.location.port;
    const isDevelopment = currentPort === "3000" || currentPort === "3001";
    const isNonLocalhost = window.location.hostname !== "localhost" && 
                           window.location.hostname !== "127.0.0.1";
    
    if (isNonLocalhost && !isDevelopment) {
      const script = document.createElement("script");
      script.src = "js/config-container.js";
      document.head.appendChild(script);
    }
  </script>
  
  <!-- Authentication Check -->
  <script>
    (function () {
      const token = localStorage.getItem("auth_token");
      if (!token && window.location.pathname !== "/login.html") {
        window.location.href = "/login.html";
      }
    })();
  </script>
  
  <!-- Auth Manager -->
  <script src="js/auth.js"></script>
</head>
<body class="nav-md">
  <!-- Gentelella template structure -->
</body>
</html>
```

### Page-Specific Features

#### Configuration Comparison (`compare.html`)
- **Three Comparison Modes:** Files, Git Commits, File History
- **Side-by-Side Diff Viewer:** Syntax highlighting and navigation
- **Export Functionality:** Download diffs as patch files
- **GitManager Integration:** Repository status and sync operations

#### Device Onboarding (`onboard-device.html`)
- **Form Validation:** Real-time validation with error states
- **Dropdown Population:** Dynamic loading from Nautobot API
- **Duplicate Detection:** IP address and device name checking
- **Job Progress Tracking:** Real-time onboarding status

#### Ansible Inventory (`ansible-inventory.html`)
- **Logical Operations Builder:** Drag-and-drop filter conditions
- **Template Selection:** Jinja2 template-based generation
- **Real-time Preview:** Live device count and inventory preview
- **Export Options:** YAML download and clipboard copy

#### Settings Applications

##### Template Management (`settings-templates.html`)
- **Multi-Source Templates:** Git repositories, file uploads, web editor
- **Template Categories:** Inventory, parser, onboarding categorization
- **Jinja2 Rendering:** Variable substitution and template preview
- **Version Control:** Template history and change tracking
- **Import/Export:** Bulk template operations with Git synchronization
- **Template Editor:** Syntax highlighting and variable extraction

##### Git Management (`settings-git.html`)
- **Repository Configuration:** URL, branch, authentication settings
- **SSL Certificate Management:** Custom CA certificates and verification options
- **Repository Health Monitoring:** Connection testing and sync status
- **Multi-Repository Support:** Different repositories for configs, templates, onboarding
- **Credential Integration:** Secure token and username storage
- **Repository Categories:** Configs, templates, onboarding rule segregation

##### Cache Management (`settings-cache.html`)
- **Performance Tuning:** TTL configuration and refresh intervals
- **Selective Caching:** Git commits, Nautobot locations, device data
- **Cache Statistics:** Hit rates and performance metrics
- **Prefetch Configuration:** Startup and background refresh settings
- **Cache Invalidation:** Manual and automatic cache clearing
- **Memory Management:** Maximum commit limits and storage optimization

## 9. Configuration Management

### Environment Detection Strategy
```javascript
// Multi-layer environment detection
1. Check for COCKPIT_API_URL environment override
2. Detect Vite development server (ports 3000/3001)
3. Look for Vite-specific DOM elements
4. Fall back to production URL construction
```

### Configuration Hierarchy
1. **Environment Variables** (highest priority)
2. **Container Configuration Override** (`config-container.js`)
3. **Base Configuration** (`config.js`)
4. **Default Values** (lowest priority)

### Development vs Production Differences
- **Development:** Relative URLs, Vite proxy, debug logging
- **Production:** Absolute URLs, optimized assets, minimal logging

## 10. Development Workflow

### Local Development Setup
```bash
# Install dependencies
npm install

# Start Vite dev server (with backend proxy)
npm run dev  # Runs on port 3000 (or 3001 if 3000 is occupied)

# Backend should be running on port 8000 for proxy to work
```

### Hot Reload Configuration
- **File Watching:** Automatic refresh on file changes
- **Proxy Integration:** Seamless API calls during development
- **Error Overlay:** Vite error display for build issues

### Development Tools
- **Browser DevTools:** Full debugging support with source maps
- **Network Tab:** Monitor API calls through Vite proxy
- **Console Logging:** Debug information in development mode

## 11. Deployment

### Production Build Process
```bash
# Build optimized assets
npm run build

# Preview production build locally
npm run preview
```

### Build Output Structure
```
dist/
├── index.html           # Entry pages
├── compare.html
├── onboard-device.html
├── scan-and-add.html
├── sync_devices.html
├── backup.html
├── ansible-inventory.html
├── settings.html        # Settings pages
├── settings-nautobot.html
├── settings-templates.html
├── settings-git.html
├── settings-cache.html
├── settings-credentials.html
├── login.html
├── js/                  # JavaScript bundles
│   ├── main-[hash].js
│   ├── vendor-core-[hash].js
│   └── vendor-charts-[hash].js
├── css/                 # CSS bundles
│   └── main-[hash].css
├── images/              # Optimized images
└── fonts/               # Web fonts
```

### Settings Applications Technical Considerations

#### Additional Build Complexity
- **Increased Entry Points:** 6 additional HTML entry points for settings pages
- **Bundle Size Growth:** Settings-specific JavaScript adds ~50KB to total bundle
- **API Surface Expansion:** 15+ additional API endpoints requiring frontend integration
- **Form Validation Complexity:** Multi-step wizards and complex validation rules

#### Browser Storage Requirements
- **Settings Caching:** localStorage for user preferences and recent configurations
- **Template Storage:** Temporary storage for draft templates and edits
- **Connection State:** Persistent storage for Git and Nautobot connection status

### Container Deployment
- **Docker Support:** Multi-stage builds with production optimizations
- **Static Serving:** Nginx or Apache for static file serving
- **Reverse Proxy:** Backend API proxying in production

## 12. Known Limitations

### Implementation Requirements for Missing Applications

The following items need to be added to fully support the settings applications:

#### Vite Configuration Updates Required
```javascript
// Additional entries needed in vite.config.js
input: {
  // Existing entries...
  backup: "production/backup.html",
  sync: "production/sync_devices.html", 
  settingsTemplates: "production/settings-templates.html",
  settingsGit: "production/settings-git.html", 
  settingsCache: "production/settings-cache.html",
  settingsCredentials: "production/settings-credentials.html"
}
```

#### Missing Frontend Dependencies
- **Syntax Highlighting:** Consider adding CodeMirror or Ace Editor for template editing
- **Git Diff Visualization:** Enhanced diff display for Git management
- **Real-time Validation:** Form validation libraries for complex settings forms
- **Progress Indicators:** Enhanced loading states for long-running operations

### Intentionally Out of Scope (Hobby Project)
- **Progressive Web App (PWA)** features
- **Service Workers** for offline functionality
- **Advanced Bundle Analysis** and optimization
- **Automated Performance Testing**
- **Cross-Browser Compatibility Testing** beyond modern browsers
- **Accessibility (a11y) Compliance** beyond basic Bootstrap standards
- **Internationalization (i18n)** support
- **Advanced Error Boundaries** and crash reporting

### Technical Limitations
- **jQuery Dependency:** Required for legacy Gentelella components
- **Multi-Page Architecture:** No client-side routing (SPA)
- **Manual Configuration:** Environment-specific URL management
- **Limited Testing:** No automated frontend testing framework
- **Template Editor Complexity:** Basic syntax highlighting without advanced IDE features
- **Cache Management UI:** Simple metrics display without detailed analytics
- **Git Integration:** Basic repository management without advanced Git workflows

### Migration Path for Advanced Features
If the project evolves beyond hobby scope:

1. **Add TypeScript** for better type safety
2. **Implement PWA** features for offline support  
3. **Add Testing Framework** (Playwright/Cypress)
4. **Migrate to SPA** with Vue.js or React
5. **Add Accessibility** compliance
6. **Implement i18n** for multiple languages

This frontend PRD provides complete implementation guidance for building the Cockpit user interface while maintaining focus on developer productivity and core functionality appropriate for a hobby project.
