#!/bin/sh
set -e

echo "Starting Cockpit container..."

# Start backend in the background
echo "Starting backend server..."
cd /app/backend
python start_isolated.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend (this will run in foreground)
echo "Starting frontend server..."
cd /app
exec npm run dev -- --host 0.0.0.0 --port 3000 --no-open
