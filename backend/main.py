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
import difflib
from pathlib import Path
import mimetypes
from datetime import datetime
from git import Repo, InvalidGitRepositoryError, GitCommandError
from .config_manual import settings

# Initialize FastAPI app
app = FastAPI(
    title="Cockpit Network Management Dashboard",
    description="A comprehensive dashboard for managing network devices via Nautobot",
    version="1.0.0"
)

# CORS middleware
print(f"Setting up CORS with origins: {settings.cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Request: {request.method} {request.url} - Origin: {request.headers.get('origin', 'None')}")
    response = await call_next(request)
    print(f"Response: {response.status_code}")
    return response

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

class FileCompareRequest(BaseModel):
    left_file: str
    right_file: str

class FileExportRequest(BaseModel):
    left_file: str
    right_file: str
    format: str = "unified"

class GitCommitRequest(BaseModel):
    message: str
    files: Optional[List[str]] = None  # If None, commit all changes

class GitBranchRequest(BaseModel):
    branch_name: str
    create: bool = False

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
            "status": "error",
            "nautobot_connection": "failed",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.get("/api/test-early")
async def test_early_endpoint():
    """Test endpoint placed early in file"""
    return {"message": "Early test endpoint working", "timestamp": datetime.now().isoformat()}

@app.get("/api/git/status-early")
async def git_status_early():
    """Early Git status endpoint"""
    return {"message": "Early Git endpoint working", "timestamp": datetime.now().isoformat()}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Cockpit API is running", "timestamp": datetime.now().isoformat()}

# Test CORS endpoint
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working", "origins": settings.cors_origins}

# Helper functions

# Enhanced response model for login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

# Authentication endpoints
@app.post("/auth/login", response_model=LoginResponse)
async def login(user_data: UserLogin):
    # For demo purposes, using simple hardcoded auth
    # In production, this should validate against a proper user database
    if user_data.username == settings.demo_username and user_data.password == settings.demo_password:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        
        # Create user data object
        user_info = {
            "username": user_data.username,
            "full_name": "Administrator",  # You can customize this
            "email": "admin@cockpit.local",
            "role": "admin"
        }
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,  # Convert to seconds
            "user": user_info
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/auth/verify")
async def verify_auth(current_user: str = Depends(verify_token)):
    return {"username": current_user, "authenticated": True}

# File management endpoints for configuration comparison
@app.get("/api/files/list")
async def list_files(current_user: str = Depends(verify_token)):
    """Get list of configuration files available for comparison"""
    try:
        config_dir = Path(settings.config_files_directory)
        
        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # If directory is empty, create sample files for demo
        if not any(config_dir.iterdir()):
            create_sample_files(config_dir)
        
        files = []
        
        # Scan the directory for configuration files
        for file_path in config_dir.rglob('*'):
            if file_path.is_file():
                # Check if file extension is allowed
                if file_path.suffix.lower() in [ext.lower() for ext in settings.allowed_file_extensions]:
                    try:
                        stat = file_path.stat()
                        relative_path = file_path.relative_to(config_dir)
                        
                        files.append({
                            "filename": file_path.name,
                            "path": str(relative_path),
                            "full_path": str(file_path),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
                            "type": "configuration",
                            "extension": file_path.suffix
                        })
                    except (OSError, PermissionError) as e:
                        print(f"Warning: Could not read file {file_path}: {e}")
                        continue
        
        # Sort files by modification time (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return {"files": files, "directory": str(config_dir.absolute())}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )

def create_sample_files(config_dir: Path):
    """Create sample configuration files for demo purposes"""
    sample_files = {
        "router-config-v1.txt": get_sample_config_content("router-config-v1.txt"),
        "router-config-v2.txt": get_sample_config_content("router-config-v2.txt"),
        "switch-config-old.txt": get_sample_config_content("switch-config-old.txt"),
        "switch-config-new.txt": get_sample_config_content("switch-config-new.txt"),
        "baseline-config.txt": get_sample_config_content("baseline-config.txt")
    }
    
    for filename, content in sample_files.items():
        file_path = config_dir / filename
        try:
            file_path.write_text(content, encoding='utf-8')
            print(f"Created sample file: {file_path}")
        except Exception as e:
            print(f"Warning: Could not create sample file {filename}: {e}")

@app.post("/api/files/compare")
async def compare_files(
    request: FileCompareRequest,
    current_user: str = Depends(verify_token)
):
    """Compare two configuration files"""
    try:
        config_dir = Path(settings.config_files_directory)
        
        # Resolve file paths
        left_file_path = config_dir / request.left_file
        right_file_path = config_dir / request.right_file
        
        # Security check: ensure files are within the config directory
        try:
            left_file_path = left_file_path.resolve()
            right_file_path = right_file_path.resolve()
            config_dir_resolved = config_dir.resolve()
            
            if not str(left_file_path).startswith(str(config_dir_resolved)):
                raise HTTPException(status_code=400, detail="Left file path is not allowed")
            if not str(right_file_path).startswith(str(config_dir_resolved)):
                raise HTTPException(status_code=400, detail="Right file path is not allowed")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file paths")
        
        # Check if files exist
        if not left_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Left file not found: {request.left_file}")
        if not right_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Right file not found: {request.right_file}")
        
        # Check file size limits
        max_size = settings.max_file_size_mb * 1024 * 1024
        if left_file_path.stat().st_size > max_size:
            raise HTTPException(status_code=413, detail=f"Left file too large (max {settings.max_file_size_mb}MB)")
        if right_file_path.stat().st_size > max_size:
            raise HTTPException(status_code=413, detail=f"Right file too large (max {settings.max_file_size_mb}MB)")
        
        # Read file contents
        try:
            left_content = left_file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encodings
            try:
                left_content = left_file_path.read_text(encoding='latin-1')
            except:
                raise HTTPException(status_code=400, detail="Could not decode left file")
        
        try:
            right_content = right_file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                right_content = right_file_path.read_text(encoding='latin-1')
            except:
                raise HTTPException(status_code=400, detail="Could not decode right file")
        
        # Create line-by-line diff
        left_lines = left_content.splitlines()
        right_lines = right_content.splitlines()
        
        # Process diff into structured format
        left_result = []
        right_result = []
        
        for i, (left_line, right_line) in enumerate(zip(left_lines, right_lines)):
            if left_line == right_line:
                left_result.append({
                    "line_number": i + 1,
                    "content": left_line,
                    "type": "equal"
                })
                right_result.append({
                    "line_number": i + 1, 
                    "content": right_line,
                    "type": "equal"
                })
            else:
                left_result.append({
                    "line_number": i + 1,
                    "content": left_line,
                    "type": "replace"
                })
                right_result.append({
                    "line_number": i + 1,
                    "content": right_line, 
                    "type": "replace"
                })
        
        # Handle different length files
        if len(left_lines) > len(right_lines):
            for i in range(len(right_lines), len(left_lines)):
                left_result.append({
                    "line_number": i + 1,
                    "content": left_lines[i],
                    "type": "delete"
                })
                right_result.append({
                    "line_number": None,
                    "content": "",
                    "type": "empty"
                })
        elif len(right_lines) > len(left_lines):
            for i in range(len(left_lines), len(right_lines)):
                left_result.append({
                    "line_number": None,
                    "content": "",
                    "type": "empty"
                })
                right_result.append({
                    "line_number": i + 1,
                    "content": right_lines[i],
                    "type": "insert"
                })
        
        return {
            "left_file": request.left_file,
            "right_file": request.right_file,
            "left_lines": left_result,
            "right_lines": right_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare files: {str(e)}"
        )

@app.post("/api/files/export-diff")
async def export_diff(
    request: FileExportRequest,
    current_user: str = Depends(verify_token)
):
    """Export diff in unified format"""
    try:
        config_dir = Path(settings.config_files_directory)
        
        # Resolve file paths
        left_file_path = config_dir / request.left_file
        right_file_path = config_dir / request.right_file
        
        # Security check: ensure files are within the config directory
        try:
            left_file_path = left_file_path.resolve()
            right_file_path = right_file_path.resolve()
            config_dir_resolved = config_dir.resolve()
            
            if not str(left_file_path).startswith(str(config_dir_resolved)):
                raise HTTPException(status_code=400, detail="Left file path is not allowed")
            if not str(right_file_path).startswith(str(config_dir_resolved)):
                raise HTTPException(status_code=400, detail="Right file path is not allowed")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file paths")
        
        # Check if files exist
        if not left_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Left file not found: {request.left_file}")
        if not right_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Right file not found: {request.right_file}")
        
        # Read file contents
        try:
            left_content = left_file_path.read_text(encoding='utf-8')
            right_content = right_file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                left_content = left_file_path.read_text(encoding='latin-1')
                right_content = right_file_path.read_text(encoding='latin-1')
            except:
                raise HTTPException(status_code=400, detail="Could not decode files")
        
        # Create unified diff
        diff_lines = list(difflib.unified_diff(
            left_content.splitlines(keepends=True),
            right_content.splitlines(keepends=True),
            fromfile=request.left_file,
            tofile=request.right_file
        ))
        
        diff_content = ''.join(diff_lines)
        filename = f"diff_{Path(request.left_file).stem}_vs_{Path(request.right_file).stem}.patch"
        
        return {
            "content": diff_content,
            "filename": filename,
            "format": request.format
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export diff: {str(e)}"
        )

@app.get("/api/files/config")
async def get_file_config(current_user: str = Depends(verify_token)):
    """Get file storage configuration information"""
    config_dir = Path(settings.config_files_directory)
    return {
        "directory": str(config_dir.absolute()),
        "directory_exists": config_dir.exists(),
        "allowed_extensions": settings.allowed_file_extensions,
        "max_file_size_mb": settings.max_file_size_mb,
        "directory_writable": config_dir.exists() and os.access(config_dir, os.W_OK)
    }

# Git management endpoints
@app.get("/api/git/status")
async def git_status(current_user: str = Depends(verify_token)):
    """Get Git repository status"""
    try:
        repo = get_git_repo()
        
        # Get current branch
        current_branch = str(repo.active_branch) if not repo.head.is_detached else "detached"
        
        # Get modified files
        modified_files = [item.a_path for item in repo.index.diff(None)]
        
        # Get untracked files
        untracked_files = repo.untracked_files
        
        # Get staged files
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        
        # Get recent commits (last 10)
        commits = []
        try:
            for commit in repo.iter_commits(max_count=10):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat(),
                    "files_changed": len(commit.stats.files)
                })
        except Exception:
            # Handle case where there are no commits yet
            pass
        
        return {
            "current_branch": current_branch,
            "modified_files": modified_files,
            "untracked_files": untracked_files,
            "staged_files": staged_files,
            "commits": commits,
            "is_dirty": repo.is_dirty()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Git status: {str(e)}"
        )

@app.post("/api/git/commit")
async def git_commit(
    request: GitCommitRequest,
    current_user: str = Depends(verify_token)
):
    """Commit changes to Git repository"""
    try:
        repo = get_git_repo()
        
        # Stage files
        if request.files:
            # Stage specific files
            repo.index.add(request.files)
        else:
            # Stage all changes
            repo.git.add(A=True)
        
        # Commit changes
        commit = repo.index.commit(request.message)
        
        return {
            "success": True,
            "commit_hash": commit.hexsha[:8],
            "message": request.message,
            "files_committed": len(commit.stats.files)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit: {str(e)}"
        )

@app.get("/api/git/branches")
async def git_branches(current_user: str = Depends(verify_token)):
    """Get list of Git branches"""
    try:
        repo = get_git_repo()
        
        branches = []
        current_branch = str(repo.active_branch) if not repo.head.is_detached else None
        
        for branch in repo.branches:
            branches.append({
                "name": str(branch),
                "is_current": str(branch) == current_branch,
                "last_commit": branch.commit.hexsha[:8],
                "last_commit_message": branch.commit.message.strip()
            })
        
        return {"branches": branches, "current_branch": current_branch}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get branches: {str(e)}"
        )

@app.post("/api/git/branch")
async def git_branch(
    request: GitBranchRequest,
    current_user: str = Depends(verify_token)
):
    """Create or switch to a Git branch"""
    try:
        repo = get_git_repo()
        
        if request.create:
            # Create new branch
            new_branch = repo.create_head(request.branch_name)
            new_branch.checkout()
            return {
                "success": True,
                "action": "created",
                "branch": request.branch_name
            }
        else:
            # Switch to existing branch
            repo.git.checkout(request.branch_name)
            return {
                "success": True,
                "action": "switched",
                "branch": request.branch_name
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to manage branch: {str(e)}"
        )

@app.get("/api/git/diff/{commit_hash}")
async def git_diff(
    commit_hash: str,
    current_user: str = Depends(verify_token)
):
    """Get diff for a specific commit"""
    try:
        repo = get_git_repo()
        
        commit = repo.commit(commit_hash)
        
        # Get diff against parent (or empty tree if first commit)
        if commit.parents:
            diff = commit.parents[0].diff(commit, create_patch=True)
        else:
            diff = commit.diff(repo.git.hash_object('-t', 'tree', '/dev/null'), create_patch=True)
        
        diffs = []
        for d in diff:
            diffs.append({
                "file": d.a_path or d.b_path,
                "change_type": d.change_type,
                "diff": str(d) if d.create_patch else ""
            })
        
        return {
            "commit": {
                "hash": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat()
            },
            "diffs": diffs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get diff: {str(e)}"
        )

@app.get("/api/git/commits/{branch_name}")
async def git_commits(
    branch_name: str,
    current_user: str = Depends(verify_token)
):
    """Get commits for a specific branch"""
    try:
        repo = get_git_repo()
        
        # Check if branch exists
        if branch_name not in [ref.name for ref in repo.refs]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch '{branch_name}' not found"
            )
        
        # Get commits from the branch
        commits = []
        for commit in repo.iter_commits(branch_name, max_count=50):
            commits.append({
                "hash": commit.hexsha,
                "message": commit.message.strip(),
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "files_changed": len(list(commit.stats.files.keys()))
            })
        
        return commits
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get commits: {str(e)}"
        )

@app.get("/api/git/files/{commit_hash}")
async def git_files(
    commit_hash: str,
    current_user: str = Depends(verify_token)
):
    """Get list of files in a specific commit"""
    try:
        repo = get_git_repo()
        
        # Get the commit
        commit = repo.commit(commit_hash)
        
        # Get all files in the commit
        files = []
        for item in commit.tree.traverse():
            if item.type == 'blob':  # Only files, not directories
                files.append(item.path)
        
        # Filter for configuration files based on allowed extensions
        config_extensions = settings.allowed_file_extensions
        config_files = [
            f for f in files 
            if any(f.endswith(ext) for ext in config_extensions)
        ]
        
        return sorted(config_files)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files: {str(e)}"
        )

@app.post("/api/git/diff")
async def git_diff_compare(
    request: dict,
    current_user: str = Depends(verify_token)
):
    """Compare files between two Git commits"""
    try:
        commit1 = request.get("commit1")
        commit2 = request.get("commit2") 
        file_path = request.get("file_path")
        
        if not all([commit1, commit2, file_path]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="commit1, commit2, and file_path are required"
            )
        
        repo = get_git_repo()
        
        # Get the commits
        commit_obj1 = repo.commit(commit1)
        commit_obj2 = repo.commit(commit2)
        
        # Get file content from both commits
        try:
            file_content1 = commit_obj1.tree[file_path].data_stream.read().decode('utf-8')
        except KeyError:
            file_content1 = ""
            
        try:
            file_content2 = commit_obj2.tree[file_path].data_stream.read().decode('utf-8')
        except KeyError:
            file_content2 = ""
        
        # Generate diff
        diff_lines = []
        import difflib
        
        lines1 = file_content1.splitlines(keepends=True)
        lines2 = file_content2.splitlines(keepends=True)
        
        for line in difflib.unified_diff(lines1, lines2, n=3):
            diff_lines.append(line.rstrip('\n'))
        
        # Calculate stats
        additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        # Prepare full file content for comparison display
        file1_lines = []
        file2_lines = []
        
        lines1_list = file_content1.splitlines()
        lines2_list = file_content2.splitlines()
        
        # Use difflib.SequenceMatcher to get line-by-line comparison
        matcher = difflib.SequenceMatcher(None, lines1_list, lines2_list)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are the same
                for i in range(i1, i2):
                    file1_lines.append({
                        "line_number": i + 1,
                        "content": lines1_list[i],
                        "type": "equal"
                    })
                for j in range(j1, j2):
                    file2_lines.append({
                        "line_number": j + 1,
                        "content": lines2_list[j],
                        "type": "equal"
                    })
            elif tag == 'delete':
                # Lines deleted from file1
                for i in range(i1, i2):
                    file1_lines.append({
                        "line_number": i + 1,
                        "content": lines1_list[i],
                        "type": "delete"
                    })
                # Add empty lines to file2 to align
                for _ in range(i1, i2):
                    file2_lines.append({
                        "line_number": None,
                        "content": "",
                        "type": "empty"
                    })
            elif tag == 'insert':
                # Lines inserted into file2
                for j in range(j1, j2):
                    file2_lines.append({
                        "line_number": j + 1,
                        "content": lines2_list[j],
                        "type": "insert"
                    })
                # Add empty lines to file1 to align
                for _ in range(j1, j2):
                    file1_lines.append({
                        "line_number": None,
                        "content": "",
                        "type": "empty"
                    })
            elif tag == 'replace':
                # Lines changed
                max_lines = max(i2 - i1, j2 - j1)
                for k in range(max_lines):
                    if k < (i2 - i1):
                        file1_lines.append({
                            "line_number": i1 + k + 1,
                            "content": lines1_list[i1 + k],
                            "type": "delete"
                        })
                    else:
                        file1_lines.append({
                            "line_number": None,
                            "content": "",
                            "type": "empty"
                        })
                    
                    if k < (j2 - j1):
                        file2_lines.append({
                            "line_number": j1 + k + 1,
                            "content": lines2_list[j1 + k],
                            "type": "insert"
                        })
                    else:
                        file2_lines.append({
                            "line_number": None,
                            "content": "",
                            "type": "empty"
                        })
        
        return {
            "commit1": commit1[:8],
            "commit2": commit2[:8],
            "file_path": file_path,
            "diff_lines": diff_lines,  # Keep for backward compatibility
            "left_file": f"{file_path} ({commit1[:8]})",
            "right_file": f"{file_path} ({commit2[:8]})",
            "left_lines": file1_lines,
            "right_lines": file2_lines,
            "stats": {
                "additions": additions,
                "deletions": deletions,
                "changes": additions + deletions,
                "total_lines": len(diff_lines)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare commits: {str(e)}"
        )

@app.get("/api/git/file-history/{file_path:path}")
async def get_file_last_change(
    file_path: str,
    current_user: str = Depends(verify_token)
):
    """Get the last change information for a specific file"""
    try:
        repo = get_git_repo()
        
        # Get the commit history for the specific file
        commits = list(repo.iter_commits(paths=file_path, max_count=1))
        
        if not commits:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No commits found for file: {file_path}"
            )
        
        last_commit = commits[0]
        
        # Check if file exists in the last commit
        try:
            file_content = (last_commit.tree / file_path).data_stream.read().decode('utf-8')
            file_exists = True
        except:
            file_exists = False
        
        return {
            "file_path": file_path,
            "file_exists": file_exists,
            "last_commit": {
                "hash": last_commit.hexsha,
                "short_hash": last_commit.hexsha[:8],
                "message": last_commit.message.strip(),
                "author": {
                    "name": last_commit.author.name,
                    "email": last_commit.author.email
                },
                "committer": {
                    "name": last_commit.committer.name,
                    "email": last_commit.committer.email
                },
                "date": last_commit.committed_datetime.isoformat(),
                "timestamp": int(last_commit.committed_datetime.timestamp())
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file history: {str(e)}"
        )

def get_sample_config_content(filename: str) -> str:
    """Generate sample configuration content for demo purposes"""
    base_config = """!
! Configuration file for network device
!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
!
hostname NetworkDevice
!
boot-start-marker
boot-end-marker
!
enable secret 5 $1$XXXX$XXXXXXXXXXXXXXXXXXXXXXXXX
!
username admin privilege 15 secret 5 $1$XXXX$XXXXXXXXXXXXXXXXXXXXXXXXX
!
interface GigabitEthernet0/0
 description Connection to Core Switch
 ip address 192.168.1.1 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/1
 description Management Interface
 ip address 10.0.1.10 255.255.255.0
 duplex auto
 speed auto
!
router ospf 1
 router-id 1.1.1.1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.1.0 0.0.0.255 area 0
!
ip route 0.0.0.0 0.0.0.0 192.168.1.254
!
access-list 10 permit 10.0.1.0 0.0.0.255
access-list 10 permit 192.168.1.0 0.0.0.255
!
snmp-server community public RO
snmp-server location "Network Closet A"
snmp-server contact "admin@company.com"
!
line con 0
 login local
line vty 0 4
 access-class 10 in
 login local
 transport input ssh
!
end"""
    
    # Modify content based on filename to create differences
    if "v2" in filename or "new" in filename:
        modified_config = base_config.replace(
            "ip address 192.168.1.1 255.255.255.0",
            "ip address 192.168.1.2 255.255.255.0"
        ).replace(
            "router-id 1.1.1.1",
            "router-id 1.1.1.2"
        ).replace(
            "snmp-server location \"Network Closet A\"",
            "snmp-server location \"Network Closet B\""
        )
        # Add a new interface in v2
        modified_config += "\n!\ninterface GigabitEthernet0/2\n description Additional Port\n shutdown\n!"
        return modified_config
    elif "switch" in filename:
        return base_config.replace("NetworkDevice", "CoreSwitch").replace(
            "hostname NetworkDevice",
            "hostname CoreSwitch"
        ).replace(
            "router ospf 1",
            "!\n! Switch configuration - no OSPF"
        ).replace(
            " router-id 1.1.1.1\n network 192.168.1.0 0.0.0.255 area 0\n network 10.0.1.0 0.0.0.255 area 0",
            ""
        )
    elif "baseline" in filename:
        return base_config.replace(
            "snmp-server community public RO",
            "! SNMP disabled for security"
        ).replace(
            "snmp-server location \"Network Closet A\"\nsnmp-server contact \"admin@company.com\"",
            ""
        )
    
    return base_config

def get_git_repo():
    """Get Git repository instance for the config directory"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        return repo
    except InvalidGitRepositoryError:
        # Try to initialize a new repo
        try:
            config_dir = Path(settings.config_files_directory)
            config_dir.mkdir(parents=True, exist_ok=True)
            repo = Repo.init(config_dir)
            return repo
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize Git repository: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git repository error: {str(e)}"
        )

@app.get("/api/debug/git")
async def debug_git(current_user: str = Depends(verify_token)):
    """Debug Git setup"""
    try:
        repo = get_git_repo()
        return {
            "status": "success",
            "repo_path": repo.working_dir,
            "branch": repo.active_branch.name
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

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

# Git-related endpoints
@app.get("/api/git/status")
async def get_git_status(current_user: str = Depends(verify_token)):
    """Get Git repository status"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        
        # Get branch info
        current_branch = repo.active_branch.name
        
        # Get status
        status_info = {
            "branch": current_branch,
            "is_dirty": repo.is_dirty(),
            "untracked_files": repo.untracked_files,
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "staged_files": [item.a_path for item in repo.index.diff("HEAD")],
        }
        
        return status_info
    except (InvalidGitRepositoryError, GitCommandError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Git repository not found or invalid: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git status error: {str(e)}"
        )

@app.get("/api/git/branches")
async def get_git_branches(current_user: str = Depends(verify_token)):
    """Get Git repository branches"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        
        branches = [branch.name for branch in repo.branches]
        return branches
    except (InvalidGitRepositoryError, GitCommandError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Git repository not found or invalid: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git branches error: {str(e)}"
        )

@app.get("/api/git/commits")
async def get_git_commits(branch: str = "main", limit: int = 50, current_user: str = Depends(verify_token)):
    """Get Git commits for a branch"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        
        commits = []
        for commit in repo.iter_commits(branch, max_count=limit):
            commits.append({
                "hash": commit.hexsha,
                "short_hash": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": {
                    "name": commit.author.name,
                    "email": commit.author.email
                },
                "date": commit.committed_datetime.isoformat(),
                "files_changed": len(commit.stats.files)
            })
        
        return commits
    except (InvalidGitRepositoryError, GitCommandError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Git repository not found or branch '{branch}' not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git commits error: {str(e)}"
        )

@app.get("/api/git/files/{commit_hash}")
async def get_git_files(commit_hash: str, current_user: str = Depends(verify_token)):
    """Get files from a specific Git commit"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        
        commit = repo.commit(commit_hash)
        files = []
        
        for item in commit.tree.traverse():
            if item.type == 'blob':  # Only files, not directories
                files.append(item.path)
        
        return sorted(files)
    except (InvalidGitRepositoryError, GitCommandError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Git repository not found or commit '{commit_hash}' not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git files error: {str(e)}"
        )

@app.get("/api/git/file-history/{file_path:path}")
async def get_file_last_change(file_path: str, current_user: str = Depends(verify_token)):
    """Get the last change information for a specific file"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        
        # Get the most recent commit that modified this file
        commits = list(repo.iter_commits(paths=file_path, max_count=1))
        
        if not commits:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No commits found for file: {file_path}"
            )
        
        latest_commit = commits[0]
        
        # Check if file exists in the latest commit
        file_exists = True
        try:
            latest_commit.tree[file_path]
        except KeyError:
            file_exists = False
        
        return {
            "file_path": file_path,
            "file_exists": file_exists,
            "last_commit": {
                "hash": latest_commit.hexsha,
                "short_hash": latest_commit.hexsha[:8],
                "message": latest_commit.message.strip(),
                "author": {
                    "name": latest_commit.author.name,
                    "email": latest_commit.author.email
                },
                "date": latest_commit.committed_datetime.isoformat()
            }
        }
    except (InvalidGitRepositoryError, GitCommandError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Git repository not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git file history error: {str(e)}"
        )

@app.get("/api/git/file-complete-history/{file_path:path}")
async def get_file_complete_history(file_path: str, from_commit: str = None, current_user: str = Depends(verify_token)):
    """Get the complete history of a file from a specific commit backwards to its creation"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        
        # Start from the specified commit or HEAD
        start_commit = from_commit if from_commit else "HEAD"
        
        # Get all commits that modified this file
        commits = list(repo.iter_commits(start_commit, paths=file_path))
        
        if not commits:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No commits found for file: {file_path}"
            )
        
        history_commits = []
        
        for i, commit in enumerate(commits):
            # Determine change type
            change_type = "M"  # Modified (default)
            
            if i == len(commits) - 1:
                # This is the first commit where the file appeared
                change_type = "A"  # Added
            else:
                # Check if the file was deleted in this commit
                try:
                    commit.tree[file_path]
                except KeyError:
                    change_type = "D"  # Deleted
            
            history_commits.append({
                "hash": commit.hexsha,
                "short_hash": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": {
                    "name": commit.author.name,
                    "email": commit.author.email
                },
                "date": commit.committed_datetime.isoformat(),
                "change_type": change_type
            })
        
        return {
            "file_path": file_path,
            "from_commit": start_commit,
            "total_commits": len(history_commits),
            "commits": history_commits
        }
        
    except (InvalidGitRepositoryError, GitCommandError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Git repository not found or commit not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git file complete history error: {str(e)}"
        )

@app.post("/api/git/diff")
async def get_git_diff(
    request: Dict[str, Any],
    current_user: str = Depends(verify_token)
):
    """Get diff between two Git commits for a specific file"""
    try:
        config_dir = Path(settings.config_files_directory)
        repo = Repo(config_dir)
        
        left_commit = request.get("left_commit")
        right_commit = request.get("right_commit")
        file_path = request.get("file_path")
        
        if not all([left_commit, right_commit, file_path]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameters: left_commit, right_commit, file_path"
            )
        
        # Get the commits
        left_commit_obj = repo.commit(left_commit)
        right_commit_obj = repo.commit(right_commit)
        
        # Get file content from both commits
        try:
            left_content = left_commit_obj.tree[file_path].data_stream.read().decode('utf-8')
        except KeyError:
            left_content = ""
        
        try:
            right_content = right_commit_obj.tree[file_path].data_stream.read().decode('utf-8')
        except KeyError:
            right_content = ""
        
        # Generate diff
        left_lines = left_content.splitlines(keepends=True)
        right_lines = right_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            left_lines, 
            right_lines,
            fromfile=f"{file_path} ({left_commit[:8]})",
            tofile=f"{file_path} ({right_commit[:8]})",
            lineterm=""
        ))
        
        return {
            "left_commit": left_commit,
            "right_commit": right_commit,
            "file_path": file_path,
            "diff": diff,
            "left_content": left_content,
            "right_content": right_content
        }
        
    except (InvalidGitRepositoryError, GitCommandError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Git repository not found or commits not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Git diff error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
