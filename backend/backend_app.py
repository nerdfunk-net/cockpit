from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import jwt
import os
from difflib import unified_diff, SequenceMatcher
import mimetypes
from pathlib import Path
import json
from datetime import datetime, timedelta, timezone
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

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CompareRequest(BaseModel):
    left_file: str
    right_file: str

class ExportRequest(BaseModel):
    left_file: str
    right_file: str
    format: str = "unified"

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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Cockpit Network Management Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "demo_credentials": {
            "username": settings.demo_username,
            "password": settings.demo_password
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Authentication endpoints
@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # Simple demo authentication - in production, use proper password hashing
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

# Protected endpoint example
@app.get("/api/profile")
async def get_profile(current_user: str = Depends(verify_token)):
    return {
        "username": current_user,
        "role": "admin",
        "message": "This is a protected endpoint"
    }

# File comparison endpoints
@app.get("/api/files/list")
async def list_files(current_user: str = Depends(verify_token)):
    """List all available configuration files for comparison"""
    try:
        # Look for configuration files in common locations
        config_paths = [
            Path("configs"),  # Local configs directory
            Path("../configs"),  # Parent directory configs
            Path("./"),  # Current directory
        ]
        
        files = []
        for config_path in config_paths:
            if config_path.exists() and config_path.is_dir():
                # Look for common config file extensions
                for pattern in ["*.txt", "*.cfg", "*.conf", "*.config", "*.ios"]:
                    for file_path in config_path.glob(pattern):
                        if file_path.is_file():
                            files.append({
                                "filename": file_path.name,
                                "path": str(file_path),
                                "size": file_path.stat().st_size,
                                "modified": file_path.stat().st_mtime
                            })
        
        # Sort by filename
        files.sort(key=lambda x: x["filename"])
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )

@app.post("/api/files/compare")
async def compare_files(request: CompareRequest, current_user: str = Depends(verify_token)):
    """Compare two configuration files and return the differences"""
    try:
        # Read the files
        left_path = Path(request.left_file)
        right_path = Path(request.right_file)
        
        if not left_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Left file not found: {request.left_file}"
            )
        
        if not right_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Right file not found: {request.right_file}"
            )
        
        # Read file contents
        with open(left_path, 'r', encoding='utf-8') as f:
            left_content = f.readlines()
        
        with open(right_path, 'r', encoding='utf-8') as f:
            right_content = f.readlines()
        
        # Generate unified diff
        diff = list(unified_diff(
            left_content,
            right_content,
            fromfile=left_path.name,
            tofile=right_path.name,
            lineterm=''
        ))
        
        # Process the diff for side-by-side comparison
        left_lines = []
        right_lines = []
        
        # Create side-by-side comparison data
        matcher = SequenceMatcher(None, left_content, right_content)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are the same
                for i in range(i1, i2):
                    left_lines.append({
                        "line_number": i + 1,
                        "content": left_content[i].rstrip('\n'),
                        "type": "equal"
                    })
                    right_lines.append({
                        "line_number": j1 + (i - i1) + 1,
                        "content": right_content[j1 + (i - i1)].rstrip('\n'),
                        "type": "equal"
                    })
            elif tag == 'delete':
                # Lines only in left file
                for i in range(i1, i2):
                    left_lines.append({
                        "line_number": i + 1,
                        "content": left_content[i].rstrip('\n'),
                        "type": "delete"
                    })
                    right_lines.append({
                        "line_number": None,
                        "content": "",
                        "type": "empty"
                    })
            elif tag == 'insert':
                # Lines only in right file
                for j in range(j1, j2):
                    left_lines.append({
                        "line_number": None,
                        "content": "",
                        "type": "empty"
                    })
                    right_lines.append({
                        "line_number": j + 1,
                        "content": right_content[j].rstrip('\n'),
                        "type": "insert"
                    })
            elif tag == 'replace':
                # Lines are different
                max_lines = max(i2 - i1, j2 - j1)
                for k in range(max_lines):
                    if k < (i2 - i1):
                        left_lines.append({
                            "line_number": i1 + k + 1,
                            "content": left_content[i1 + k].rstrip('\n'),
                            "type": "replace"
                        })
                    else:
                        left_lines.append({
                            "line_number": None,
                            "content": "",
                            "type": "empty"
                        })
                    
                    if k < (j2 - j1):
                        right_lines.append({
                            "line_number": j1 + k + 1,
                            "content": right_content[j1 + k].rstrip('\n'),
                            "type": "replace"
                        })
                    else:
                        right_lines.append({
                            "line_number": None,
                            "content": "",
                            "type": "empty"
                        })
        
        return {
            "left_file": left_path.name,
            "right_file": right_path.name,
            "left_lines": left_lines,
            "right_lines": right_lines,
            "unified_diff": diff
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing files: {str(e)}"
        )

@app.post("/api/files/export-diff")
async def export_diff(request: ExportRequest, current_user: str = Depends(verify_token)):
    """Export the diff in the requested format"""
    try:
        # Read the files
        left_path = Path(request.left_file)
        right_path = Path(request.right_file)
        
        if not left_path.exists() or not right_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both files not found"
            )
        
        # Read file contents
        with open(left_path, 'r', encoding='utf-8') as f:
            left_content = f.readlines()
        
        with open(right_path, 'r', encoding='utf-8') as f:
            right_content = f.readlines()
        
        if request.format == "unified":
            # Generate unified diff
            diff_lines = list(unified_diff(
                left_content,
                right_content,
                fromfile=left_path.name,
                tofile=right_path.name,
                lineterm=''
            ))
            content = '\n'.join(diff_lines)
            filename = f"diff_{left_path.stem}_vs_{right_path.stem}.patch"
            
        elif request.format == "side-by-side":
            # Generate side-by-side comparison
            content_lines = []
            content_lines.append(f"File Comparison: {left_path.name} vs {right_path.name}")
            content_lines.append("=" * 80)
            content_lines.append("")
            
            matcher = SequenceMatcher(None, left_content, right_content)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    for i in range(i1, i2):
                        content_lines.append(f"  {i+1:4d} | {left_content[i].rstrip()}")
                elif tag == 'delete':
                    for i in range(i1, i2):
                        content_lines.append(f"- {i+1:4d} | {left_content[i].rstrip()}")
                elif tag == 'insert':
                    for j in range(j1, j2):
                        content_lines.append(f"+ {j+1:4d} | {right_content[j].rstrip()}")
                elif tag == 'replace':
                    for i in range(i1, i2):
                        content_lines.append(f"- {i+1:4d} | {left_content[i].rstrip()}")
                    for j in range(j1, j2):
                        content_lines.append(f"+ {j+1:4d} | {right_content[j].rstrip()}")
            
            content = '\n'.join(content_lines)
            filename = f"comparison_{left_path.stem}_vs_{right_path.stem}.txt"
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use 'unified' or 'side-by-side'"
            )
        
        return {
            "content": content,
            "filename": filename,
            "format": request.format
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting diff: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=settings.port)
