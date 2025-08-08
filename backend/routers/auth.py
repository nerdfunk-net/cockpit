"""
Authentication router for login and token management.
"""

from __future__ import annotations
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from models.auth import UserLogin, LoginResponse
from core.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin):
    """
    Authenticate user and return JWT token.
    
    For demo purposes, using simple hardcoded auth.
    In production, this should validate against a proper user database.
    """
    from config import settings
    
    if user_data.username == settings.demo_username and user_data.password == settings.demo_password:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user={
                "username": user_data.username,
                "role": "admin" if user_data.username == settings.demo_username else "user"
            }
        )
    
    # Try guest login
    elif user_data.username == "guest" and user_data.password == "guest":
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer", 
            expires_in=settings.access_token_expire_minutes * 60,
            user={
                "username": user_data.username,
                "role": "guest"
            }
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh")
async def refresh_token(current_user: str = None):
    """Refresh JWT token (placeholder for future implementation)."""
    # This would be implemented for token refresh functionality
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented yet"
    )
