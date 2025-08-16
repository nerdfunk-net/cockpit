# Database Settings Integration

This update modifies the Cockpit backend to use database-stored settings instead of only environment variables for Nautobot API calls.

## Changes Made

### 1. Modified `main.py`

- Added `get_nautobot_config()` function that prioritizes database settings over environment variables
- Updated all Nautobot API functions to use database settings:
  - `nautobot_request()`
  - `nautobot_graphql_query()`
  - Device sync endpoints
  - Root endpoint
- Added new test endpoint `/api/nautobot/test` to verify current configuration
- Added logging to show which configuration source is being used

### 2. Enhanced `settings_manager.py`

- Now uses environment variables as initial defaults when creating the database
- Improved error handling and fallback mechanisms

### 3. Updated `start.py`

- Added database initialization on startup
- Automatically populates database with environment variables if no settings exist
- Better startup logging

### 4. Updated `backend/Dockerfile`

- Now uses `start.py` instead of direct uvicorn command
- Ensures proper database initialization

## How It Works

1. **Startup**: Database is initialized with environment variables if empty
2. **API Calls**: System checks database first, falls back to environment variables
3. **Settings Updates**: Web interface updates are now effective immediately
4. **Fallback**: If database is unavailable, environment variables are used

## Testing

Use the test script to verify configuration:

```bash
cd backend
python test_config.py
```

Test API endpoint:

```bash
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/api/nautobot/test
```

## Environment Variables (Fallback)

These are still used as defaults and fallback:

- `NAUTOBOT_HOST`
- `NAUTOBOT_TOKEN`
- `NAUTOBOT_TIMEOUT`

## Database Settings (Primary)

Settings are stored in SQLite database at:
`data/settings/cockpit_settings.db`

Managed via web interface at Settings page.
