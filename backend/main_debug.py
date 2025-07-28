"""
Debug version of main.py to identify import issues.
"""

from __future__ import annotations
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("Starting main.py execution...")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("Logging configured")

# Initialize FastAPI app
app = FastAPI(
    title="Cockpit API",
    description="Network Device Management Dashboard API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
print("FastAPI app created")

# CORS configuration
def setup_cors():
    """Configure CORS middleware."""
    try:
        print("Setting up CORS...")
        from config_manual import settings
        print("Config imported")
        
        # Get CORS origins from config
        cors_origins = settings.cors_origins
        if isinstance(cors_origins, str):
            cors_origins = [origins.strip() for origins in cors_origins.split(",")]
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            headers=["*"],
        )
        print("CORS configured successfully")
    except Exception as e:
        print(f"CORS setup failed: {e}")
        import traceback
        traceback.print_exc()

print("About to setup CORS...")
setup_cors()

print("About to import routers...")
try:
    # Import routers
    from routers.auth import router as auth_router
    from routers.nautobot import router as nautobot_router
    from routers.git import router as git_router
    from routers.files import router as files_router
    from routers.settings import router as settings_router
    print("All routers imported successfully")

    # Include routers
    app.include_router(auth_router)
    app.include_router(nautobot_router)
    app.include_router(git_router)
    app.include_router(files_router)
    app.include_router(settings_router)
    print("All routers included successfully")

except Exception as e:
    print(f"Router import/include failed: {e}")
    import traceback
    traceback.print_exc()

print("Main.py execution completed")
print(f"App object: {app}")
