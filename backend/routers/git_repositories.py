"""
Git repositories management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from models.git_repositories import (
    GitRepositoryRequest,
    GitRepositoryResponse,
    GitRepositoryListResponse,
    GitRepositoryUpdateRequest,
    GitConnectionTestRequest,
    GitConnectionTestResponse,
    GitSyncRequest,
    GitSyncResponse
)
from git_repositories_manager import GitRepositoryManager
from core.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/git-repositories", tags=["git-repositories"])

# Initialize git repository manager
git_repo_manager = GitRepositoryManager()


@router.get("", response_model=GitRepositoryListResponse)
async def get_repositories(
    category: Optional[str] = None,
    active_only: bool = False,
    current_user: dict = Depends(verify_token)
):
    """Get all git repositories."""
    try:
        repositories = git_repo_manager.get_repositories(category=category, active_only=active_only)
        
        # Convert to response models (excluding sensitive data like tokens)
        repo_responses = []
        for repo in repositories:
            repo_dict = dict(repo)
            # Remove token from response for security
            repo_dict.pop('token', None)
            repo_responses.append(GitRepositoryResponse(**repo_dict))
        
        return GitRepositoryListResponse(
            repositories=repo_responses,
            total=len(repo_responses)
        )
    except Exception as e:
        logger.error(f"Error getting repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}", response_model=GitRepositoryResponse)
async def get_repository(
    repo_id: int,
    current_user: dict = Depends(verify_token)
):
    """Get a specific git repository by ID."""
    try:
        repository = git_repo_manager.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Remove token from response for security
        repo_dict = dict(repository)
        repo_dict.pop('token', None)
        
        return GitRepositoryResponse(**repo_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting repository {repo_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=GitRepositoryResponse)
async def create_repository(
    repository: GitRepositoryRequest,
    current_user: dict = Depends(verify_token)
):
    """Create a new git repository."""
    try:
        repo_data = repository.dict()
        repo_id = git_repo_manager.create_repository(repo_data)
        
        # Get the created repository
        created_repo = git_repo_manager.get_repository(repo_id)
        if not created_repo:
            raise HTTPException(status_code=500, detail="Failed to retrieve created repository")
        
        # Remove token from response for security
        repo_dict = dict(created_repo)
        repo_dict.pop('token', None)
        
        return GitRepositoryResponse(**repo_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{repo_id}", response_model=GitRepositoryResponse)
async def update_repository(
    repo_id: int,
    repository: GitRepositoryUpdateRequest,
    current_user: dict = Depends(verify_token)
):
    """Update a git repository."""
    try:
        # Check if repository exists
        existing_repo = git_repo_manager.get_repository(repo_id)
        if not existing_repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Update only provided fields
        repo_data = {k: v for k, v in repository.dict().items() if v is not None}
        
        if not repo_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = git_repo_manager.update_repository(repo_id, repo_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update repository")
        
        # Get the updated repository
        updated_repo = git_repo_manager.get_repository(repo_id)
        if not updated_repo:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated repository")
        
        # Remove token from response for security
        repo_dict = dict(updated_repo)
        repo_dict.pop('token', None)
        
        return GitRepositoryResponse(**repo_dict)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating repository {repo_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{repo_id}")
async def delete_repository(
    repo_id: int,
    hard_delete: bool = True,
    current_user: dict = Depends(verify_token)
):
    """Delete a git repository."""
    try:
        # Check if repository exists
        existing_repo = git_repo_manager.get_repository(repo_id)
        if not existing_repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        success = git_repo_manager.delete_repository(repo_id, hard_delete=hard_delete)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete repository")
        
        action = "deleted" if hard_delete else "deactivated"
        return {"message": f"Repository {action} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting repository {repo_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=GitConnectionTestResponse)
async def test_git_connection(
    test_request: GitConnectionTestRequest,
    current_user: dict = Depends(verify_token)
):
    """Test git repository connection."""
    try:
        # Import git functionality
        import subprocess
        import tempfile
        import os
        from pathlib import Path
        
        # Create temporary directory for test
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test_repo"
            
            # Build git clone command
            clone_url = test_request.url
            if test_request.username and test_request.token:
                # Add authentication to URL
                if "://" in clone_url:
                    protocol, rest = clone_url.split("://", 1)
                    clone_url = f"{protocol}://{test_request.username}:{test_request.token}@{rest}"
            
            # Set up environment
            env = os.environ.copy()
            if not test_request.verify_ssl:
                env["GIT_SSL_NO_VERIFY"] = "1"
            
            # Try to clone (shallow clone for speed)
            cmd = [
                "git", "clone", 
                "--depth", "1",
                "--branch", test_request.branch,
                clone_url,
                str(test_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                return GitConnectionTestResponse(
                    success=True,
                    message="Git connection successful",
                    details={
                        "branch": test_request.branch,
                        "url": test_request.url
                    }
                )
            else:
                return GitConnectionTestResponse(
                    success=False,
                    message=f"Git connection failed: {result.stderr}",
                    details={
                        "error": result.stderr,
                        "return_code": result.returncode
                    }
                )
                
    except subprocess.TimeoutExpired:
        return GitConnectionTestResponse(
            success=False,
            message="Git connection test timed out",
            details={"error": "Connection timeout after 30 seconds"}
        )
    except Exception as e:
        logger.error(f"Error testing git connection: {e}")
        return GitConnectionTestResponse(
            success=False,
            message=f"Git connection test error: {str(e)}",
            details={"error": str(e)}
        )


@router.post("/{repo_id}/sync")
async def sync_repository(
    repo_id: int,
    current_user: dict = Depends(verify_token)
):
    """Sync a git repository."""
    try:
        # Check if repository exists
        repository = git_repo_manager.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Update sync status to indicate sync started
        git_repo_manager.update_sync_status(repo_id, "syncing")
        
        # TODO: Implement actual sync logic here
        # For now, just mark as synced
        git_repo_manager.update_sync_status(repo_id, "synced")
        
        return {"message": "Repository synced successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing repository {repo_id}: {e}")
        git_repo_manager.update_sync_status(repo_id, f"error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=GitSyncResponse)
async def sync_repositories(
    sync_request: GitSyncRequest,
    current_user: dict = Depends(verify_token)
):
    """Sync git repositories."""
    try:
        if sync_request.repository_id:
            # Sync specific repository
            repos = [git_repo_manager.get_repository(sync_request.repository_id)]
            if not repos[0]:
                raise HTTPException(status_code=404, detail="Repository not found")
        else:
            # Sync all active repositories
            repos = git_repo_manager.get_repositories(active_only=True)
        
        synced = []
        failed = []
        errors = {}
        
        for repo in repos:
            try:
                repo_id = repo['id']
                git_repo_manager.update_sync_status(repo_id, "syncing")
                
                # TODO: Implement actual sync logic here
                # For now, just mark as synced
                git_repo_manager.update_sync_status(repo_id, "synced")
                synced.append(repo_id)
            except Exception as e:
                repo_id = repo['id']
                failed.append(repo_id)
                errors[str(repo_id)] = str(e)
                git_repo_manager.update_sync_status(repo_id, f"error: {str(e)}")
        
        message = f"Synced {len(synced)} repositories"
        if failed:
            message += f", {len(failed)} failed"
        
        return GitSyncResponse(
            synced_repositories=synced,
            failed_repositories=failed,
            errors=errors,
            message=message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(current_user: dict = Depends(verify_token)):
    """Health check for git repository management."""
    try:
        health = git_repo_manager.health_check()
        return health
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
