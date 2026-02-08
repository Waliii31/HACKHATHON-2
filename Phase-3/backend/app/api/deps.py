"""
API Dependencies for Phase III.

Provides common dependencies for route handlers including authentication.
"""
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from typing import Optional
from app.config import settings


async def get_current_user_id(
    authorization: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")
) -> str:
    """
    Extract and verify user ID from JWT token.
    
    This dependency validates the JWT token from the Authorization header
    and returns the user_id claim.
    
    For development/testing, if X-User-Id header is provided (and in development mode),
    it is used directly. Otherwise, if no token is provided, a test user ID is returned.
    
    Args:
        authorization: Bearer token from Authorization header
        x_user_id: Optional user ID for development override
        
    Returns:
        User ID string (UUID)
        
    Raises:
        HTTPException 401 if token is missing or invalid
    """
    # Development mode: allow requests with X-User-Id header or no auth
    if settings.ENVIRONMENT == "development":
        if x_user_id:
            return x_user_id
        if not authorization:
            return "00000000-0000-0000-0000-000000000001"
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = parts[1]
    
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user_id from payload
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Token missing user identifier"
            )
        
        return user_id
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user_id(
    authorization: Optional[str] = Header(default=None)
) -> Optional[str]:
    """
    Optionally extract user ID from JWT token.
    
    Returns None if no token is provided, otherwise validates and returns user_id.
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user_id(authorization)
    except HTTPException:
        return None
