# Cockpit - Network Device Management Dashboard

## Architecture Overview

**Cockpit** is a network device management dashboard built as a dual-stack application:
- **Frontend**: Gentelella Bootstrap template with Vite build system, serving static pages from `production/`
- **Backend**: FastAPI server with Git-based configuration management and Nautobot API integration
- **Core Purpose**: Compare device configurations across Git commits, file systems, and live history

### Key Components

1. **Configuration Comparison Engine** (`production/compare.html` + backend Git endpoints)
   - Three comparison modes: Files, Git Commits, File History
   - Git-backed diff visualization with commit-based navigation
   - File search with regex support across repository history

2. **Authentication System** (`production/js/auth.js` + JWT backend)
   - localStorage-based session management
   - Demo credentials: admin/admin, guest/guest
   - AuthManager class handles token lifecycle
   - **Smart URL routing**: Auto-detects development/production for API calls
   - **Vite proxy integration**: Uses relative URLs in development mode

3. **Settings Management** (`backend/settings_manager.py`)
   - SQLite-based configuration storage
   - Nautobot and Git repository settings
   - Runtime configuration updates without restart

## Development Workflow

### Local Development Setup
```bash
# Frontend (Vite dev server - tries :3000, falls back to :3001)
npm install && npm run dev

# Backend (FastAPI with auto-reload on :8000)  
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Docker Development
```bash
# Full stack deployment
cp .env.docker .env  # Configure NAUTOBOT_HOST, NAUTOBOT_TOKEN, SECRET_KEY
./docker-start.sh    # Frontend :3000, Backend :8000
```

### Development Server Details
- **Frontend**: Vite dev server with hot reload, proxy configured for `/api` and `/auth`
- **Backend**: FastAPI with auto-reload, accessible at `http://localhost:8000`
- **Port Conflicts**: If 3000 is occupied, Vite automatically uses 3001
- **API Proxy**: Development requests to `/api/*` are proxied to backend automatically

### VS Code Tasks
- **"Run FastAPI backend (Uvicorn)"** - Starts backend with virtual environment

## Docker Container Management

### Container Setup
```bash
# Build and start containers
docker-compose up --build

# Run in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f cockpit-frontend
docker-compose logs -f cockpit-backend
```

### Container Configuration
- **Frontend Container**: Serves files via Vite dev server on port 3000
- **Backend Container**: FastAPI application on port 8000
- **Volume Mounts**: `./configs` mapped to container for persistent Git repository
- **Environment Variables**: Configure via `.env` file or docker-compose override

### Common Docker Issues
- **Port Conflicts**: Ensure ports 3000 and 8000 are available
- **Permission Issues**: Check file permissions for volume mounts
- **Environment Variables**: Verify `.env` file is properly configured
- **Container Logs**: Use `docker-compose logs` to debug startup issues

## Project-Specific Patterns

### Configuration Management
- **Manual Config**: `backend/config_manual.py` uses simple environment variables (preferred)
- **Settings Persistence**: SQLite database at `backend/settings/cockpit_settings.db`
- **Git Integration**: Repository consistency requires all Git endpoints use `get_git_repo()` helper

### Frontend Architecture
- **Authentication Check**: Every page has inline auth verification before DOM load
- **API Communication**: `window.authManager.apiRequest()` method handles all API calls with automatic authentication
- **Development vs Production URLs**: AuthManager automatically detects development mode (ports 3000/3001) and uses relative URLs for Vite proxy
- **Module Loading**: Vite builds from `src/main*.js` entry points, serves via `production/` static files
- **Repository Management**: GitManager class handles all Git repository status and operations via UI section

### GitManager Class (`compare.html`)
- **Purpose**: Manages Git repository status, sync, and clone operations in the UI
- **Auto-initialization**: Waits for AuthManager to be ready before checking repository status
- **Status Panel**: "Git Repository Status" section with collapsible interface
- **API Integration**: Uses `/api/git/repo/status`, `/api/git/repo/sync`, `/api/git/repo/clone`
- **Auto-collapse**: Automatically hides status panel when repository is ready and configured
- **Error Handling**: Provides user-friendly messages for Git operation failures

### Backend API Patterns
- **Repository Access**: Always use `get_git_repo()` for Git operations to ensure consistency
- **Error Handling**: FastAPI HTTPException with appropriate status codes
- **CORS**: Configured for localhost development, customizable via environment
- **Router Structure**: APIs organized in `/backend/routers/` (git.py, nautobot.py, etc.)
- **Authentication**: JWT tokens via `/auth/login`, all API endpoints require authentication

### Git Operations
- **File History**: `/api/git/file-complete-history/{file_path}` provides commit timeline
- **Branch Management**: Dynamic branch switching with `/api/git/branches` and `/api/git/commits`
- **Diff Generation**: Unified diff format via `/api/git/diff` POST endpoint

## Critical Integration Points

### Nautobot API Integration
- GraphQL queries for device, location, and namespace data
- JWT-based authentication with configurable token expiry
- Connection testing via `/api/nautobot/test` endpoint

### File System Structure
```
production/        # Static frontend files (HTML, CSS, JS)
src/              # Vite source files and SCSS
backend/          # FastAPI application
backend/settings/ # SQLite database storage
```

### Environment Configuration
```bash
# Required for production
NAUTOBOT_HOST=https://your-nautobot.com
NAUTOBOT_TOKEN=your-api-token
SECRET_KEY=your-jwt-secret

# Development defaults
DEBUG=true
SERVER_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

## Common Debugging Patterns

### Git Repository Issues
- Repository consistency errors: Check all Git endpoints use `get_git_repo()`
- "Bad object" errors: Verify repository path consistency across API endpoints
- File history not loading: Ensure File History mode uses same endpoints as Git Commits mode

### Authentication Issues
- Check browser localStorage for `auth_token` and `user_info`
- AuthManager initialization timing in `compare.html` includes multiple retry mechanisms
- Cross-tab session sync via storage event listeners

### Configuration Comparison
- Three-mode system requires endpoint consistency
- File search initialization timing critical in mode switching
- Commit display formatting uses manual hash substring for "undefined" prevention

## Critical Development Guidelines

### API URL Management
- **NEVER hardcode URLs** like `http://localhost:8000` in frontend code
- **ALWAYS use** `window.authManager.apiRequest('/api/endpoint')` for API calls
- **Development Detection**: AuthManager auto-detects ports 3000/3001 for Vite proxy
- **Relative URLs**: In development, use `/api/endpoint` to leverage Vite proxy configuration

### Error Handling Best Practices
- **Check API endpoints exist** before implementing frontend calls
- **Use backend router grep searches** to verify endpoint availability
- **Remove redundant validation systems** - avoid duplicate functionality
- **Test with curl** to verify backend endpoints work before frontend integration

### Vite Development Setup
- **Frontend runs on port 3001** (if 3000 is occupied)
- **Backend runs on port 8000** 
- **Vite proxy configuration** forwards `/api` and `/auth` to backend
- **Never bypass proxy** with absolute URLs in development

### Code Replacement Guidelines
- **Include 3-5 lines context** when using replace_string_in_file
- **Check for duplicate code blocks** after replacements
- **Verify syntax** especially for JavaScript brace matching
- **Test immediately** after major refactoring changes

### Common JavaScript Pitfalls
- **Duplicate catch blocks**: When replacing try/catch, ensure no duplicate catch statements
- **Missing closing braces**: Always verify brace matching after large refactors
- **Async/await consistency**: Don't mix .then() and async/await patterns
- **AuthManager timing**: Always check `window.authManager` exists before use

### Backend Endpoint Verification
- **Grep search first**: Use `grep_search` to find existing endpoints before implementing
- **Router organization**: Check `/backend/routers/` for API structure
- **Avoid 404 errors**: Verify endpoint exists with curl testing before frontend integration
- **Use existing patterns**: Follow established endpoint naming conventions

## Backend Development Details

### FastAPI Server Management
```bash
# Standard startup (from backend directory)
python -m uvicorn main:app --reload

# Alternative startup methods
python start.py                    # Uses start.py wrapper
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Debug mode with additional logging
python -m uvicorn main:app --reload --log-level debug
```

### Backend Dependencies
- **Virtual Environment**: Always use `.venv` for isolation
- **Requirements**: Install with `pip install -r requirements.txt`
- **Git Dependencies**: Requires Git installed on system for repository operations
- **Database**: SQLite database created automatically in `backend/settings/`

### Common Backend Startup Issues
- **Port 8000 in use**: Check for other FastAPI/Django applications
- **Import errors**: Ensure virtual environment is activated and dependencies installed
- **Git operations failing**: Verify Git is installed and repository path is accessible
- **Authentication errors**: Check JWT secret key configuration

# Python Development Instructions

## Project Overview
This project follows modern Python best practices with emphasis on clean, maintainable, and well-tested code.

## Code Style & Formatting
- **Follow PEP 8** style guidelines strictly
- Use **4 spaces** for indentation (no tabs)
- Maximum line length of **88 characters** (Black formatter standard)
- Use **double quotes** for strings unless single quotes avoid escaping
- Import organization: standard library → third-party → local imports

## Type Hints & Documentation
- **Always use type hints** for function parameters and return values
- Use `from __future__ import annotations` for forward references
- Include **docstrings** for all public functions, classes, and modules using Google style format:

```python
def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.

    Args:
        radius: The radius of the circle in meters.

    Returns:
        The area of the circle in square meters.

    Raises:
        ValueError: If radius is negative.
    """
    if radius < 0:
        raise ValueError("Radius must be non-negative")
    return math.pi * radius ** 2
```
## Default Credentials

- The default username and password for the app are:
  - **Username:** admin
  - **Password:** admin
