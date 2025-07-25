#!/usr/bin/env python3
"""
Cockpit Backend Startup Script
Loads configuration and starts the FastAPI server.
"""

import uvicorn
from config_manual import settings
import logging

def main():
    """Start the FastAPI server with configuration."""
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Log startup information
    logger.info("Starting Cockpit Backend Server")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"Debug: {settings.debug}")
    logger.info(f"Nautobot: {settings.nautobot_url}")
    logger.info(f"CORS Origins: {settings.cors_origins}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()
