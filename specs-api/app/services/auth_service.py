from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
from typing import Optional
from ..core.database_factory import get_database
from ..models.auth import UserCreate, UserResponse, Token, UserLogin, UserScopesResponse


class AuthService:
    def __init__(self):
        self.db = get_database()
    
    def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        if self.db.create_user(user_data.username, user_data.email, user_data.password):
            created_user = self.db.get_user(user_data.username)
            if created_user:
                # Get user scopes (will be empty for new user)
                user_scopes = self.get_user_scopes_by_id(created_user["id"])
                
                return UserResponse(
                    id=created_user["id"],
                    username=created_user["username"],
                    email=created_user["email"],
                    is_active=created_user["is_active"],
                    role=created_user.get("role", "user"),
                    available_scopes=user_scopes,
                    created_at=created_user["created_at"]
                )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    def login_user(self, user_credentials: UserLogin) -> Token:
        """Login user and return JWT token with requested scopes"""
        user = self.db.authenticate_user(user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate and filter requested scopes
        valid_scopes = self.db.validate_scopes(user_credentials.scopes, user)
        
        access_token_expires = timedelta(minutes=30)
        access_token = self.db.create_access_token(
            data={"sub": user["username"], "scopes": valid_scopes}, 
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer", scopes=valid_scopes)
    
    def get_current_user_from_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """Get current user from JWT token with scopes"""
        token = credentials.credentials
        token_data = self.db.verify_token(token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = self.db.get_user(token_data["username"])
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Add scopes to user data
        user["scopes"] = token_data["scopes"]
        return user
    
    def get_user_profile(self, current_user: dict) -> UserResponse:
        """Get current user profile"""
        # Get user scopes
        user_scopes = self.get_user_scopes_by_id(current_user["id"])
        
        return UserResponse(
            id=current_user["id"],
            username=current_user["username"],
            email=current_user["email"],
            is_active=current_user["is_active"],
            role=current_user.get("role", "user"),
            available_scopes=user_scopes,
            created_at=current_user["created_at"]
        )
    
    def get_protected_message(self, current_user: dict) -> dict:
        """Get protected route message"""
        return {"message": f"Hello {current_user['username']}, this is a protected route!"}
    
    def get_health_status(self) -> dict:
        """Get API health status"""
        return {"message": "ECS Auth API is running!"}
    
    def get_available_scopes(self) -> dict:
        """Get all available scopes"""
        return self.db.get_available_scopes()
    
    def check_scope_permission(self, current_user: dict, required_scope: str) -> bool:
        """Check if current user has required scope"""
        user_scopes = current_user.get("scopes", [])
        return required_scope in user_scopes
    
    def get_user_scopes(self, current_user: dict) -> dict:
        """Get current user's scope information"""
        return {
            "username": current_user["username"],
            "available_scopes": current_user.get("available_scopes", []),
            "current_token_scopes": current_user.get("scopes", [])
        }
    
    def get_user_scopes_by_id(self, user_id: int) -> list:
        """Get user scopes by user ID"""
        # Use the database's built-in method which handles different SQL dialects
        return self.db.get_user_available_scopes(user_id)
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        return self.db.get_user_by_id(user_id)
    
    def grant_scope_to_user(self, user_id: int, scope: str, granted_by: str) -> bool:
        """Grant a scope to a user (admin only)"""
        available_scopes = list(self.db.get_available_scopes().keys())
        if scope not in available_scopes:
            return False
        return self.db.grant_scope_to_user(user_id, scope, granted_by)
    
    def revoke_scope_from_user(self, user_id: int, scope: str) -> bool:
        """Revoke a scope from a user (admin only)"""
        return self.db.revoke_scope_from_user(user_id, scope)
    
    def list_all_users_with_scopes(self) -> list:
        """List all users with their scopes (admin only)"""
        return self.db.list_all_users_with_scopes()
