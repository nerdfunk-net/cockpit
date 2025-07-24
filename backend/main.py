from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import jwt
import requests
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import os
from config_manual import settings

# Initialize FastAPI app
app = FastAPI(
    title="Cockpit Network Management Dashboard",
    description="A comprehensive dashboard for managing network devices via Nautobot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class DeviceFilter(BaseModel):
    location: Optional[str] = None
    device_type: Optional[str] = None
    status: Optional[str] = None

# JWT functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Nautobot API helper functions
def nautobot_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make a request to Nautobot API"""
    url = f"{settings.nautobot_url.rstrip('/')}/api/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Token {settings.nautobot_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Nautobot API error: {str(e)}"
        )

def nautobot_graphql_query(query: str, variables: dict = None) -> dict:
    """Execute a GraphQL query against Nautobot"""
    url = f"{settings.nautobot_url.rstrip('/')}/api/graphql/"
    headers = {
        "Authorization": f"Token {settings.nautobot_token}",
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Nautobot GraphQL error: {str(e)}"
        )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Cockpit Network Management Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "nautobot_url": settings.nautobot_url
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Test Nautobot connectivity
        nautobot_request("dcim/devices/?limit=1")
        return {
            "status": "healthy",
            "nautobot_connection": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "nautobot_connection": "failed",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Authentication endpoints
@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # For demo purposes, using simple hardcoded auth
    # In production, this should validate against a proper user database
    if user_data.username == settings.demo_username and user_data.password == settings.demo_password:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/auth/verify")
async def verify_auth(current_user: str = Depends(verify_token)):
    return {"username": current_user, "authenticated": True}

# Device management endpoints
@app.get("/api/devices")
async def get_devices(
    limit: int = 50,
    offset: int = 0,
    current_user: str = Depends(verify_token)
):
    """Get list of devices from Nautobot"""
    try:
        endpoint = f"dcim/devices/?limit={limit}&offset={offset}"
        result = nautobot_request(endpoint)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch devices: {str(e)}"
        )

@app.get("/api/devices/{device_id}")
async def get_device(device_id: str, current_user: str = Depends(verify_token)):
    """Get specific device details from Nautobot"""
    try:
        endpoint = f"dcim/devices/{device_id}/"
        result = nautobot_request(endpoint)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch device {device_id}: {str(e)}"
        )

@app.post("/api/devices/search")
async def search_devices(
    filters: DeviceFilter,
    current_user: str = Depends(verify_token)
):
    """Search devices with filters"""
    try:
        query_params = []
        if filters.location:
            query_params.append(f"location={filters.location}")
        if filters.device_type:
            query_params.append(f"device_type={filters.device_type}")
        if filters.status:
            query_params.append(f"status={filters.status}")
        
        query_string = "&".join(query_params)
        endpoint = f"dcim/devices/?{query_string}" if query_string else "dcim/devices/"
        
        result = nautobot_request(endpoint)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search devices: {str(e)}"
        )

# Location endpoints
@app.get("/api/locations")
async def get_locations(current_user: str = Depends(verify_token)):
    """Get list of locations from Nautobot"""
    try:
        result = nautobot_request("dcim/locations/")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch locations: {str(e)}"
        )

# Device types endpoints
@app.get("/api/device-types")
async def get_device_types(current_user: str = Depends(verify_token)):
    """Get list of device types from Nautobot"""
    try:
        result = nautobot_request("dcim/device-types/")
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch device types: {str(e)}"
        )

# Interface endpoints
@app.get("/api/devices/{device_id}/interfaces")
async def get_device_interfaces(device_id: str, current_user: str = Depends(verify_token)):
    """Get interfaces for a specific device"""
    try:
        endpoint = f"dcim/interfaces/?device_id={device_id}"
        result = nautobot_request(endpoint)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch interfaces for device {device_id}: {str(e)}"
        )

# GraphQL endpoint for complex queries
@app.post("/api/graphql")
async def graphql_query(
    query_data: dict,
    current_user: str = Depends(verify_token)
):
    """Execute GraphQL query against Nautobot"""
    try:
        query = query_data.get("query")
        variables = query_data.get("variables", {})
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GraphQL query is required"
            )
        
        result = nautobot_graphql_query(query, variables)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GraphQL query failed: {str(e)}"
        )

# Statistics endpoint
@app.get("/api/stats")
async def get_statistics(current_user: str = Depends(verify_token)):
    """Get dashboard statistics"""
    try:
        # Get device counts by status
        devices = nautobot_request("dcim/devices/")
        locations = nautobot_request("dcim/locations/")
        device_types = nautobot_request("dcim/device-types/")
        
        stats = {
            "total_devices": devices.get("count", 0),
            "total_locations": locations.get("count", 0),
            "total_device_types": device_types.get("count", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
