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
- **CORS Support** - Configured for frontend-backend communication
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
- **CORS Middleware** - Cross-origin request handling

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

| Variable | Description | Example |
|----------|-------------|---------|
| `NAUTOBOT_HOST` | Nautobot URL | `https://nautobot.example.com` |
| `NAUTOBOT_TOKEN` | API token | `abc123...` |
| `SECRET_KEY` | JWT secret | `your-secret-key` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost,https://app.com` |

## ⚙️ Configuration

### Backend Configuration

The backend uses environment variables for configuration. Copy the example configuration file and modify it:

```bash
cd backend
cp .env.example .env
```

#### Environment Variables (`.env` file)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SERVER_HOST` | Backend server host | `127.0.0.1` | No |
| `SERVER_PORT` | Backend server port | `8000` | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `NAUTOBOT_HOST` | Nautobot instance URL | `http://localhost:8080` | **Yes** |
| `NAUTOBOT_TOKEN` | Nautobot API token | - | **Yes** |
| `NAUTOBOT_TIMEOUT` | Request timeout (seconds) | `30` | No |
| `SECRET_KEY` | JWT signing key | - | **Yes** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000,http://localhost:5173` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

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
CORS_ORIGINS=http://localhost:3000,https://your-frontend.example.com
LOG_LEVEL=INFO
```

### Frontend Configuration

Frontend configuration is handled in `src/config.js`. You can modify:

- **API_CONFIG**: Backend URL, endpoints, timeouts
- **UI_CONFIG**: Pagination, table settings, filters
- **SECURITY_CONFIG**: Token storage, session timeouts

#### Example Frontend Configuration
```javascript
// API Configuration
export const API_CONFIG = {
  BASE_URL: 'https://api.your-domain.com',  // Your backend URL
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
};

// UI Configuration  
export const UI_CONFIG = {
  PAGE_SIZE: 25,  // Items per page
  FILTERS: {
    NAME_MIN_LENGTH: 2,  // Minimum characters for name filter
    LOCATION_MIN_LENGTH: 2
  }
};
```

### Default Login Credentials
The application comes with a default admin user:
- **Username:** `admin`, **Password:** `admin`

> ⚠️ **Security Notice:** Change default password and secret key in production!

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