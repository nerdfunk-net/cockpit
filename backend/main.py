from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
import json
import os

app = FastAPI()

# Authentication configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simple user storage (in production, use a database)
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "email": "admin@example.com",
        "full_name": "Administrator"
    },
    "demo": {
        "username": "demo",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "email": "demo@example.com", 
        "full_name": "Demo User"
    }
}

security = HTTPBearer(auto_error=False)

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nautobot connection settings
NAUTOBOT_HOST = "http://localhost:8080"
NAUTOBOT_TOKEN = "0123456789abcdef0123456789abcdef01234567"

# Authentication helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    try:
        return bcrypt.verify(plain_password, hashed_password)
    except:
        # Fallback for simple comparison during development
        return plain_password == "secret"

def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        return bcrypt.hash(password)
    except:
        # Fallback for development
        return password

def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    user = USERS_DB.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except:
        # Fallback for development without jwt library
        username = data.get("sub", "unknown")
        return f"token-{username}-{datetime.utcnow().timestamp()}"

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Try to decode JWT token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except:
        # Fallback for development tokens
        if not credentials.credentials.startswith("token-"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        username = credentials.credentials.split("-")[1]
    
    user = USERS_DB.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user



from fastapi import Query, Body
import ipaddress
from typing import Optional
import sys

# Authentication endpoints
@app.post("/api/auth/login")
def login(credentials: dict = Body(...)):
    """Authenticate user and return access token"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password required"
        )
    
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"]
        }
    }

@app.post("/api/auth/register")
def register(user_data: dict = Body(...)):
    """Register a new user"""
    username = user_data.get("username")
    password = user_data.get("password")
    email = user_data.get("email")
    full_name = user_data.get("full_name", "")
    
    if not username or not password or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username, password, and email required"
        )
    
    if username in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Hash password and store user
    hashed_password = get_password_hash(password)
    USERS_DB[username] = {
        "username": username,
        "hashed_password": hashed_password,
        "email": email,
        "full_name": full_name
    }
    
    # Return token for immediate login
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": username,
            "email": email,
            "full_name": full_name
        }
    }

@app.get("/api/auth/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"]
    }

# Protected routes - add authentication dependency
@app.get("/api/devices")
def get_devices(
    filter_type: Optional[str] = Query(None), 
    filter_value: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {NAUTOBOT_TOKEN}"
    }
    payload = None
    # Only use the GraphQL queries provided by the user for all filter types
    if filter_type == "name" and filter_value and len(filter_value) >= 3:
        # Use ONLY the provided GraphQL query for device name
        query = '''query single_device($device_filter: [String]) {\n  devices(name__re: $device_filter) {\n    id\n    name\n    role { name }\n    location { name }\n    primary_ip4 { address }\n    status { name }\n  }\n}'''
        variables = {"device_filter": [filter_value]}
        payload = {"query": query, "variables": variables}
    elif filter_type == "location" and filter_value and len(filter_value) >= 3:
        # Use ONLY the provided GraphQL query for location
        query = '''query devives_in_location($location_filter: [String]) {\n  locations(name__re: $location_filter) {\n    name\n    devices {\n      id\n      name\n      role { name }\n      location { name }\n      primary_ip4 { address }\n      status { name }\n    }\n  }\n}'''
        variables = {"location_filter": [filter_value]}
        payload = {"query": query, "variables": variables}
    elif filter_type == "prefix" and filter_value and filter_value.count('.') == 3:
        # Use ONLY the provided GraphQL query for prefix
        query = '''query devices_by_ip_prefix($prefix_filter: [String]) {\n  prefixes(within_include: $prefix_filter) {\n    prefix\n    ip_addresses {\n      primary_ip4_for {\n        id\n        name\n        role { name }\n        location { name }\n        primary_ip4 { address }\n        status { name }\n      }\n    }\n  }\n}'''
        variables = {"prefix_filter": [filter_value]}
        payload = {"query": query, "variables": variables}
    else:
        # No valid filter provided, return empty list
        print(f"[DEBUG] Invalid or missing filter_type/filter_value: filter_type={filter_type}, filter_value={filter_value}")
        sys.stdout.flush()
        return JSONResponse(content={"devices": []})
    try:
        resp = requests.post(f"{NAUTOBOT_HOST}/api/graphql/", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if filter_type == "prefix":
            # Extract devices from primary_ip4_for, avoid duplicates
            devices = []
            seen_ids = set()
            for prefix in data.get("data", {}).get("prefixes", []):
                for ip in prefix.get("ip_addresses", []):
                    devs = ip.get("primary_ip4_for")
                    if isinstance(devs, list):
                        for dev in devs:
                            if dev and dev.get("id") and dev["id"] not in seen_ids:
                                devices.append({
                                    "id": dev.get("id"),
                                    "name": dev.get("name"),
                                    "role": dev.get("role"),
                                    "location": dev.get("location"),
                                    "primary_ip4": dev.get("primary_ip4"),
                                    "status": dev.get("status")
                                })
                                seen_ids.add(dev["id"])
                    elif isinstance(devs, dict):
                        dev = devs
                        if dev and dev.get("id") and dev["id"] not in seen_ids:
                            devices.append({
                                "id": dev.get("id"),
                                "name": dev.get("name"),
                                "role": dev.get("role"),
                                "location": dev.get("location"),
                                "primary_ip4": dev.get("primary_ip4"),
                                "status": dev.get("status")
                            })
                            seen_ids.add(dev["id"])
        elif filter_type == "location":
            # Extract devices from locations, avoid duplicates
            devices = []
            seen_ids = set()
            for loc in data.get("data", {}).get("locations", []):
                for dev in loc.get("devices", []):
                    if dev and dev.get("id") and dev["id"] not in seen_ids:
                        devices.append({
                            "id": dev.get("id"),
                            "name": dev.get("name"),
                            "role": dev.get("role"),
                            "location": dev.get("location"),
                            "primary_ip4": dev.get("primary_ip4"),
                            "status": dev.get("status")
                        })
                        seen_ids.add(dev["id"])
        else:
            devices = data.get("data", {}).get("devices", [])
        return JSONResponse(content={"devices": devices})
    except Exception as e:
        print(f"[ERROR] Exception in get_devices: {e}")
        sys.stdout.flush()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/statuses")
def get_statuses(current_user: dict = Depends(get_current_user)):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {NAUTOBOT_TOKEN}"
    }
    query = '''query status { statuses { id name } }'''
    payload = {"query": query}
    try:
        resp = requests.post(f"{NAUTOBOT_HOST}/api/graphql/", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        statuses = data.get("data", {}).get("statuses", [])
        # Return list of {id, name}
        return JSONResponse(content={"statuses": statuses})
    except Exception as e:
        print(f"[ERROR] Exception in get_statuses: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/namespaces")
def get_namespaces(current_user: dict = Depends(get_current_user)):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {NAUTOBOT_TOKEN}"
    }
    query = '''query namespace { namespaces { id name } }'''
    payload = {"query": query}
    try:
        resp = requests.post(f"{NAUTOBOT_HOST}/api/graphql/", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        namespaces = data.get("data", {}).get("namespaces", [])
        return JSONResponse(content={"namespaces": namespaces})
    except Exception as e:
        print(f"[ERROR] Exception in get_namespaces: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/sync-network-data")
def sync_network_data(payload: dict = Body(...), current_user: dict = Depends(get_current_user)):
    # Compose the Nautobot job URL
    url = f"{NAUTOBOT_HOST}/api/extras/jobs/Sync%20Network%20Data%20From%20Network/run/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {NAUTOBOT_TOKEN}"
    }
    # Add body_format: json as required
    body = {"body_format": "json", "data": payload.get("data", {})}
    print("[DEBUG] Nautobot Sync Request URL:", url)
    print("[DEBUG] Nautobot Sync Request Headers:", headers)
    print("[DEBUG] Nautobot Sync Request Body:", body)
    sys.stdout.flush()
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=30)
        resp.raise_for_status()
        print("[DEBUG] Nautobot Sync Response:", resp.text)
        sys.stdout.flush()
        return JSONResponse(content=resp.json())
    except Exception as e:
        print(f"[ERROR] Exception in sync_network_data: {e}")
        sys.stdout.flush()
        return JSONResponse(content={"error": str(e)}, status_code=500)
