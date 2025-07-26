# Docker Setup

Simple Docker setup for Cockpit application.

## Quick Start

1. Copy the environment file:
   ```bash
   cp .env.docker .env
   ```

2. Edit `.env` with your Nautobot configuration:
   - Set `NAUTOBOT_HOST` to your Nautobot instance
   - Set `NAUTOBOT_TOKEN` to your API token
   - Change `SECRET_KEY` to a secure value

3. Start the application:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Services

- **Frontend**: Vite development server with production build
- **Backend**: FastAPI server with Nautobot integration

## Environment Variables

See `.env.docker` for all available configuration options.

## Local Static Assets

The application includes local FontAwesome assets in `/production/static/` so it works without external CDN dependencies.
