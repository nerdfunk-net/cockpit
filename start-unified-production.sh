#!/bin/sh
set -e

echo "Starting Cockpit unified container (production mode)..."

# Start backend in the background
echo "Starting backend server..."
cd /app/backend
python start.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend in preview mode (serves built assets)
echo "Starting frontend preview server..."
cd /app
exec npm run preview -- --host 0.0.0.0 --port 3000
