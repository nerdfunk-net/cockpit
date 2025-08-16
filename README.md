# Cockpit - Network Device Management Dashboard

A modern web-based dashboard for managing network devices through Nautobot API integration. Built with the Gentelella Bootstrap admin template and FastAPI backend, this application provides an intuitive interface for network engineers to synchronize, filter, and manage network infrastructure devices.

## 🚀 Features

### Frontend Dashboard

- **Modern Bootstrap 5 UI** - Clean, responsive admin interface based on Gentelella template
- **Device Synchronization** - Interactive dual-pane interface for device selection and management
- **Advanced Filtering** - Filter devices by name (regex), location, or IP prefix (CIDR)
- **Real-time Updates** - Dynamic device data fetching with instant feedback
- **Authentication System** - Secure JWT-based user authentication
- **Multiple Dashboard Layouts** - 3 different dashboard styles for various use cases

### Backend API

- **FastAPI Framework** - High-performance async Python API
- **Nautobot Integration** - GraphQL queries to fetch device, location, and namespace data
- **JWT Authentication** - Secure token-based authentication system
- **Vite Proxy Integration** - Seamless frontend-backend communication without CORS complexity
- **RESTful Endpoints** - Clean API design for device management operations

### Device Management

- **Device Discovery** - Query devices from Nautobot by multiple criteria
- **Network Synchronization** - Bulk sync network data from devices to Nautobot
- **Location-based Filtering** - Find devices by location patterns
- **IP-based Queries** - Search devices by IP prefix/subnet
- **Batch Operations** - Select and process multiple devices simultaneously

## 🛠️ Technology Stack

### Frontend

- **Bootstrap 5** - Modern CSS framework
- **Vite** - Fast build tool and dev server
- **JavaScript ES6+** - Modern JavaScript features
- **jQuery & jQuery UI** - Enhanced user interactions
- **Chart.js & ECharts** - Data visualization
- **DataTables** - Advanced table functionality
- **FontAwesome** - Icon library

### Backend

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **JWT Authentication** - JSON Web Token security
- **Requests** - HTTP client for Nautobot API
- **Vite Proxy Support** - Simplified development without CORS middleware

### External Integrations

- **Nautobot** - Network source of truth platform
- **GraphQL** - Efficient data querying

## 📋 Prerequisites

### For Local Development

- **Node.js** (v16 or higher)
- **Python** (3.8 or higher)
- **Nautobot instance** with GraphQL API access
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### For Docker Deployment

- **Docker** (20.10 or higher)
- **Docker Compose** (v2.0 or higher)
- **Nautobot instance** with GraphQL API access

## 🚀 Installation

### Option 1: Docker Deployment (Recommended)

Docker deployment is the easiest way to run Cockpit with all dependencies included.

```bash
# 1. Clone the repository
git clone <repository-url>
cd cockpit

# 2. Configure environment variables
cp .env.docker .env
# Edit .env file with your Nautobot settings:
# - NAUTOBOT_HOST=https://your-nautobot-instance.com
# - NAUTOBOT_TOKEN=your-api-token
# - SECRET_KEY=your-secret-key

# 3. Start with Docker Compose
./docker-start.sh
# Or manually:
# docker-compose up -d
```

The application will be available at:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Option 2: Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd cockpit
```

### 2. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file and update the following required settings:
# NAUTOBOT_HOST=http://your-nautobot-instance:8080
# NAUTOBOT_TOKEN=your-api-token
# SECRET_KEY=your-secret-key-for-production

# Start the backend server
python start.py
# Or for development with auto-reload:
python -m uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000` (or your configured port)

### 4. Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# 1. Clone and configure
git clone <repository-url>
cd cockpit
cp .env.docker .env

# 2. Edit .env file with your settings
# NAUTOBOT_HOST=https://your-nautobot.example.com
# NAUTOBOT_TOKEN=your-api-token
# SECRET_KEY=your-secret-key

# 3. Start containers
./docker-start.sh
```

### Docker Commands

```bash
# Start containers
./docker-start.sh
# or: docker-compose up -d

# Stop containers
./docker-start.sh stop
# or: docker-compose down

# View logs
./docker-start.sh logs
# or: docker-compose logs -f

# Check status
./docker-start.sh status
# or: docker-compose ps

# Restart containers
./docker-start.sh restart
```

### Docker Environment Variables

All configuration is handled via environment variables in Docker:

| Variable         | Description   | Example                        |
| ---------------- | ------------- | ------------------------------ |
| `NAUTOBOT_HOST`  | Nautobot URL  | `https://nautobot.example.com` |
| `NAUTOBOT_TOKEN` | API token     | `abc123...`                    |
| `SECRET_KEY`     | JWT secret    | `your-secret-key`              |
| `DEBUG`          | Debug mode    | `false`                        |
| `LOG_LEVEL`      | Logging level | `INFO`                         |

## ⚙️ Configuration

### Backend Configuration

The backend uses environment variables for configuration. Copy the example configuration file and modify it:

```bash
cd backend
cp .env.example .env
```

#### Environment Variables (`.env` file)

| Variable                      | Description               | Default                 | Required |
| ----------------------------- | ------------------------- | ----------------------- | -------- |
| `SERVER_HOST`                 | Backend server host       | `127.0.0.1`             | No       |
| `SERVER_PORT`                 | Backend server port       | `8000`                  | No       |
| `DEBUG`                       | Enable debug mode         | `false`                 | No       |
| `NAUTOBOT_HOST`               | Nautobot instance URL     | `http://localhost:8080` | **Yes**  |
| `NAUTOBOT_TOKEN`              | Nautobot API token        | -                       | **Yes**  |
| `NAUTOBOT_TIMEOUT`            | Request timeout (seconds) | `30`                    | No       |
| `SECRET_KEY`                  | JWT signing key           | -                       | **Yes**  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration          | `30`                    | No       |
| `LOG_LEVEL`                   | Logging level             | `INFO`                  | No       |

#### Example Configuration

```bash
# Required Settings
NAUTOBOT_HOST=https://your-nautobot.example.com
NAUTOBOT_TOKEN=0123456789abcdef0123456789abcdef01234567
SECRET_KEY=your-super-secret-key-change-this-in-production

# Optional Settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
NAUTOBOT_TIMEOUT=30
ACCESS_TOKEN_EXPIRE_MINUTES=60
LOG_LEVEL=INFO
```

### Frontend Configuration

Frontend configuration is handled in `production/js/config.js`. This file contains environment-specific settings for API URLs, endpoints, and debugging options.

#### Configuration File Location

- **File:** `production/js/config.js`
- **Purpose:** Centralized configuration for frontend-backend communication
- **Scope:** URL management, environment detection, debug settings

#### Configuration Variables

| Variable                    | Description           | Default                         | Environment |
| --------------------------- | --------------------- | ------------------------------- | ----------- |
| `api.baseUrl`               | Backend API base URL  | Auto-detected based on protocol | All         |
| `frontend.baseUrl`          | Frontend base URL     | Auto-detected from current host | All         |
| `environment.isDevelopment` | Development mode flag | Auto-detected from hostname     | All         |
| `debug.enabled`             | Enable debug logging  | `true` in development           | All         |

#### Configuration Options

**Option 1: Auto-detection (Default)**

```javascript
api: {
  baseUrl: window.location.protocol === 'https:'
    ? 'https://localhost:8000'  // Use HTTPS in production
    : 'http://localhost:8000',  // Use HTTP in development
}
```

**Option 2: Host-based detection**

```javascript
api: {
  // Alternative: detect from current host
  baseUrl: `${window.location.protocol}//${window.location.hostname}:8000`,
}
```

**Option 3: Environment-specific URLs**

```javascript
api: {
  baseUrl: window.location.hostname === 'localhost'
    ? 'http://localhost:8000'                    // Development
    : 'https://api.your-domain.com',            // Production
}
```

#### Production Deployment Configuration

For production deployment, edit `production/js/config.js`:

1. **Update the API base URL** to point to your production backend:

```javascript
const CockpitConfig = {
  api: {
    baseUrl: "https://api.your-domain.com", // Your production backend URL
    // ... rest of configuration
  },
};
```

2. **Configure HTTPS** for secure environments:

```javascript
api: {
  baseUrl: window.location.protocol === 'https:'
    ? 'https://api.your-domain.com'     // Production HTTPS
    : 'http://localhost:8000',          // Development HTTP
}
```

3. **Environment-specific settings**:

```javascript
// Production example
api: {
  baseUrl: 'https://api.production.com',
}

// Staging example
api: {
  baseUrl: 'https://api.staging.com',
}

// Development example
api: {
  baseUrl: 'http://localhost:8000',
}
```

#### Helper Functions

The configuration provides helper functions for URL generation:

```javascript
// Get full API URL for any endpoint
const loginUrl = CockpitConfig.getApiUrl("/auth/login");
// Returns: https://api.your-domain.com/auth/login

// Get frontend URL with path
const dashboardUrl = CockpitConfig.getFrontendUrl("/dashboard.html");
// Returns: https://your-frontend.com/dashboard.html
```

#### Environment Detection

The configuration automatically detects the environment:

```javascript
// Check environment
if (CockpitConfig.environment.isDevelopment) {
  console.log("Running in development mode");
}

// Debug logging (enabled automatically in development)
if (CockpitConfig.debug.enabled) {
  console.log("Debug mode enabled");
}
```

#### Files That Use Configuration

The following files automatically use the configuration from `config.js`:

- `production/onboard-device.html` - Device onboarding form
- `production/js/auth.js` - Authentication system
- `production/login.html` - Login page
- Any other frontend components that make API calls

> **Note:** The configuration file must be included in HTML pages before other JavaScript files that depend on it.

### Default Login Credentials

The application comes with a default admin user:

- **Username:** `admin`, **Password:** `admin`

> ⚠️ **Security Notice:** Change default password and secret key in production!

## 🚀 Deployment Checklist

### Before Production Deployment

**Backend Configuration (`backend/.env`):**

1. ✅ Set `NAUTOBOT_HOST` to your Nautobot instance URL
2. ✅ Set `NAUTOBOT_TOKEN` to your API token
3. ✅ Generate and set a secure `SECRET_KEY`
4. ✅ Set `DEBUG=false` for production
5. ✅ Set appropriate `LOG_LEVEL` (INFO or WARNING)

**Frontend Configuration (`production/js/config.js`):**

1. ✅ Update `api.baseUrl` to your production backend URL
2. ✅ Ensure HTTPS is used in production environments
3. ✅ Verify all endpoint paths are correct
4. ✅ Test configuration with helper functions

**Security Settings:**

1. ✅ Change default admin password (`admin`/`admin`)
2. ✅ Use strong, unique `SECRET_KEY` for JWT signing
3. ✅ Enable HTTPS for production deployments
4. ✅ Disable debug mode in production

**Example Production Configuration:**

`backend/.env`:

```bash
NAUTOBOT_HOST=https://nautobot.company.com
NAUTOBOT_TOKEN=your-secure-api-token-here
SECRET_KEY=your-very-secure-secret-key-for-jwt-signing
DEBUG=false
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

`production/js/config.js`:

```javascript
const CockpitConfig = {
  api: {
    baseUrl: "https://api.cockpit.company.com", // Your production API
    // ... rest of configuration
  },
};
```

## 📖 Usage

### Device Synchronization

1. **Login** to the dashboard using default credentials
2. **Navigate** to the "Sync Devices" page
3. **Apply Filters:**
   - **Name Filter:** Use regex patterns to match device names
   - **Location Filter:** Search devices by location name
   - **Prefix Filter:** Use CIDR notation (e.g., `192.168.1.0/24`)
4. **Select Devices** from the left panel using checkboxes
5. **Move Selected** devices to the right panel for processing
6. **Configure Sync** parameters (status, namespace)
7. **Execute Sync** to update Nautobot with network data

### API Endpoints

#### Authentication

- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info

#### Device Management

- `GET /api/nautobot/devices` - List devices with optional filtering
  - `?filter_type=name&filter_value=pattern` - Filter by device name
  - `?filter_type=location&filter_value=location` - Filter by location
  - `?filter_type=prefix&filter_value=192.168.1.0/24` - Filter by IP prefix

#### Network Operations

- `GET /api/nautobot/namespaces` - List available namespaces
- `POST /api/nautobot/sync-network-data` - Sync network data to Nautobot

## 🏗️ Project Structure

```
cockpit/
├── backend/              # FastAPI backend
│   ├── main.py          # Main API application
│   ├── config.py        # Configuration management
│   ├── start.py         # Server startup script
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Example environment config
│   └── .env             # Environment variables (create from .env.example)
├── docker/              # Docker configuration
│   └── nginx.conf       # Nginx configuration for frontend
├── production/          # Production HTML pages
│   ├── index.html       # Main dashboard
│   ├── sync_devices.html # Device sync interface
│   └── js/              # JavaScript modules
├── src/                 # Source files
│   ├── main.js          # Main application entry
│   ├── config.js        # Frontend configuration
│   ├── main.scss        # Styling
│   └── modules/         # Reusable modules
├── docs/                # Documentation
├── Dockerfile.backend   # Backend Docker configuration
├── Dockerfile.frontend  # Frontend Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── docker-start.sh      # Docker startup script
├── .env.docker          # Docker environment template
├── package.json         # Node.js dependencies
├── vite.config.js       # Vite configuration
└── README.md           # This file
```

## 🔧 Development

### Running in Development Mode

```bash
# Terminal 1: Start backend with auto-reload
cd backend
cp .env.example .env  # Configure your settings
python -m uvicorn main:app --reload

# Terminal 2: Start frontend
npm run dev
```

### Available VS Code Tasks

- **Run FastAPI backend (Uvicorn)** - Starts the backend server with configuration

### Building for Production

```bash
npm run build
```

## 📝 License

This project is based on the Gentelella Admin Template by Colorlib and is available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:

- Check the documentation in the `docs/` folder
- Review the API integration guide
- Examine the component reference

---

**Made with ❤️ for Network Engineers**
