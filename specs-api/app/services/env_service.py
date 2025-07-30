from fastapi import HTTPException, status
from typing import List, Optional
from ..core.database_factory import get_database

class EnvironmentService:
    def __init__(self):
        self.db = get_database()
    
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
