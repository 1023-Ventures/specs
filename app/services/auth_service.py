from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
from ..core.database import Database
from ..models.auth import UserCreate, UserResponse, Token, UserLogin


class AuthService:
    def __init__(self):
        self.db = Database()
    
    def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        if self.db.create_user(user_data.username, user_data.email, user_data.password):
            created_user = self.db.get_user(user_data.username)
            if created_user:
                return UserResponse(
                    id=created_user["id"],
                    username=created_user["username"],
                    email=created_user["email"],
                    is_active=created_user["is_active"],
                    created_at=created_user["created_at"]
                )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    def login_user(self, user_credentials: UserLogin) -> Token:
        """Login user and return JWT token"""
        user = self.db.authenticate_user(user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = self.db.create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    
    def get_current_user_from_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """Get current user from JWT token"""
        token = credentials.credentials
        username = self.db.verify_token(token)
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = self.db.get_user(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    
    def get_user_profile(self, current_user: dict) -> UserResponse:
        """Get current user profile"""
        return UserResponse(
            id=current_user["id"],
            username=current_user["username"],
            email=current_user["email"],
            is_active=current_user["is_active"],
            created_at=current_user["created_at"]
        )
    
    def get_protected_message(self, current_user: dict) -> dict:
        """Get protected route message"""
        return {"message": f"Hello {current_user['username']}, this is a protected route!"}
    
    def get_health_status(self) -> dict:
        """Get API health status"""
        return {"message": "ECS Auth API is running!"}
