#!/usr/bin/env python3
"""Simple server launcher for the refactored Cockpit app."""

import sys
import os

# Change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Add backend directory to Python path
sys.path.insert(0, backend_dir)

print(f"Changed to directory: {os.getcwd()}")
print(f"Python path includes: {backend_dir}")

try:
    # Import the app
    from main import app
    print("✅ Successfully imported FastAPI app")
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    sys.exit(1)

import uvicorn
from config import settings

if __name__ == "__main__":
    print("Starting Cockpit API server...")
    print(f"Server will run on http://0.0.0.0:{settings.port}")

    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=settings.port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)
