from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
from typing import Optional
from ..core.database import Database
from ..models.auth import UserCreate, UserResponse, Token, UserLogin, UserScopesResponse, EnvVarCreate, EnvVarResponse, EnvVarListResponse


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
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, is_active, role, created_at
            FROM users WHERE id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "is_active": bool(row[3]),
                "role": row[4],
                "created_at": row[5]
            }
            user["available_scopes"] = self.db.get_user_available_scopes(user_id)
            return user
        return None
    
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
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.role, u.is_active,
                   GROUP_CONCAT(us.scope) as scopes
            FROM users u
            LEFT JOIN user_scopes us ON u.id = us.user_id
            GROUP BY u.id, u.username, u.email, u.role, u.is_active
        """)
        
        users = []
        for row in cursor.fetchall():
            scopes = row[5].split(',') if row[5] else []
            users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3],
                "is_active": bool(row[4]),
                "available_scopes": scopes
            })
        
        conn.close()
        return users
    
    # Environment Variables service methods
    def get_user_env_vars(self, current_user: dict) -> dict:
        """Get all environment variables for the current user"""
        env_vars = self.db.get_user_env_vars(current_user["id"])
        return {
            "variables": env_vars,
            "total_count": len(env_vars),
            "username": current_user["username"]
        }
    
    def get_user_env_var(self, name: str, current_user: dict) -> dict:
        """Get a specific environment variable for the current user"""
        env_var = self.db.get_user_env_var(current_user["id"], name)
        if not env_var:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Environment variable '{name}' not found"
            )
        return env_var
    
    def set_user_env_var(self, name: str, value: str, current_user: dict) -> dict:
        """Set/update an environment variable for the current user"""
        if self.db.set_user_env_var(current_user["id"], name, value):
            return {
                "message": f"Environment variable '{name}' set successfully",
                "name": name,
                "value": value,
                "username": current_user["username"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to set environment variable"
            )
    
    def delete_user_env_var(self, name: str, current_user: dict) -> dict:
        """Delete an environment variable for the current user"""
        if self.db.delete_user_env_var(current_user["id"], name):
            return {
                "message": f"Environment variable '{name}' deleted successfully",
                "name": name,
                "username": current_user["username"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Environment variable '{name}' not found"
            )
