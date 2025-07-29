# FastAPI Backend

This is a minimal FastAPI backend for your cockpit frontend project.

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Endpoints

- `GET /ping` — Health check endpoint, returns `{ "message": "pong" }`

## API Access

All API endpoints require JWT authentication. The frontend uses Vite proxy during development, eliminating the need for CORS configuration.
