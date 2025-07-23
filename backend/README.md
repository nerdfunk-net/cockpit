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

## CORS

CORS is enabled for all origins for development. Adjust `allow_origins` in `main.py` for production use.
