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

3. **Settings Management** (`backend/settings_manager.py`)
   - SQLite-based configuration storage
   - Nautobot and Git repository settings
   - Runtime configuration updates without restart

## Development Workflow

### Local Development Setup
```bash
# Frontend (Vite dev server on :3000)
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

### VS Code Tasks
- **"Run FastAPI backend (Uvicorn)"** - Starts backend with virtual environment

## Project-Specific Patterns

### Configuration Management
- **Manual Config**: `backend/config_manual.py` uses simple environment variables (preferred)
- **Settings Persistence**: SQLite database at `backend/settings/cockpit_settings.db`
- **Git Integration**: Repository consistency requires all Git endpoints use `get_git_repo()` helper

### Frontend Architecture
- **Authentication Check**: Every page has inline auth verification before DOM load
- **API Communication**: `ApiManager` class wraps fetch calls with config-based endpoints
- **Module Loading**: Vite builds from `src/main*.js` entry points, serves via `production/` static files

### Backend API Patterns
- **Repository Access**: Always use `get_git_repo()` for Git operations to ensure consistency
- **Error Handling**: FastAPI HTTPException with appropriate status codes
- **CORS**: Configured for localhost development, customizable via environment

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
