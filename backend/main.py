"""
Main FastAPI application for Cockpit network device management dashboard.

This is the refactored main application file that uses modular routers
for better code organization and maintainability.
"""

from __future__ import annotations
import logging
from datetime import datetime
from fastapi import FastAPI, Depends

# Import routers
from routers.auth import router as auth_router
from routers.nautobot import router as nautobot_router
from routers.git import router as git_router
from routers.files import router as files_router
from routers.settings import router as settings_router
from routers.templates import router as templates_router
from routers.git_repositories import router as git_repositories_router
from routers.ansible_inventory import router as ansible_inventory_router

# Import auth dependency
from core.auth import verify_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cockpit API",
    description="Network Device Management Dashboard API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False
)

# Include routers
app.include_router(auth_router)
app.include_router(nautobot_router)
app.include_router(git_router)
app.include_router(files_router)
app.include_router(settings_router)
app.include_router(templates_router)
app.include_router(git_repositories_router)
app.include_router(ansible_inventory_router)

# Health check and basic endpoints
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Cockpit API v2.0 - Network Device Management Dashboard",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint."""
    return {
        "message": "Test endpoint working", 
        "timestamp": datetime.now().isoformat()
    }


# Legacy compatibility endpoints that might still be used by frontend
@app.get("/api/stats")
async def get_statistics():
    """
    Get dashboard statistics - legacy endpoint.
    Redirects to Nautobot stats.
    """
    # Import here to avoid circular imports
    from routers.nautobot import get_nautobot_stats
    from core.auth import verify_token
    from fastapi import Depends
    
    # This would need token verification in a real implementation
    # For now, just return basic stats
    return {
        "message": "Use /api/nautobot/stats for detailed statistics",
        "timestamp": datetime.now().isoformat()
    }


# GraphQL endpoint compatibility
@app.post("/api/graphql")
async def graphql_endpoint(query_data: dict, current_user: str = Depends(verify_token)):
    """
    Legacy GraphQL endpoint - maintains backward compatibility.
    Forwards requests to the Nautobot GraphQL service.
    """
    from services.nautobot import nautobot_service
    from fastapi import HTTPException, status
    
    try:
        query = query_data.get("query")
        variables = query_data.get("variables", {})
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GraphQL query is required"
            )
        
        result = await nautobot_service.graphql_query(query, variables)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GraphQL query failed: {str(e)}"
        )


@app.post("/api/nautobot/graphql")  
async def nautobot_graphql_endpoint(query_data: dict):
    """
    Execute GraphQL query against Nautobot - compatibility endpoint.
    
    This endpoint maintains backward compatibility with existing frontend code.
    """
    from services.nautobot import nautobot_service
    from fastapi import HTTPException, status
    
    try:
        query = query_data.get("query")
        variables = query_data.get("variables", {})
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GraphQL query is required"
            )
        
        result = await nautobot_service.graphql_query(query, variables)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GraphQL query failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    from config_manual import settings
    
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
