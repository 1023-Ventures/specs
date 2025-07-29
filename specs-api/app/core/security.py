from fastapi import HTTPException, status, Depends
from functools import wraps
from typing import List
from ..services.auth_service import AuthService

# Initialize auth service
auth_service = AuthService()

def require_scopes(required_scopes: List[str]):
    """Decorator to require specific scopes for an endpoint"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs (should be injected by dependency)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_scopes = current_user.get("scopes", [])
            
            # Check if user has any of the required scopes
            if not any(scope in user_scopes for scope in required_scopes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required scopes: {required_scopes}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_scope_access(current_user: dict, required_scope: str) -> bool:
    """Utility function to check if user has required scope"""
    user_scopes = current_user.get("scopes", [])
    return required_scope in user_scopes
