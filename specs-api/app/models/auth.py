from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    available_scopes: List[str] = []
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    scopes: List[str] = []

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class UserLogin(BaseModel):
    username: str
    password: str
    scopes: List[str] = []  # Requested scopes

class ScopeRequest(BaseModel):
    """Request to grant/revoke scopes"""
    user_id: int
    scope: str
    action: str  # "grant" or "revoke"

class UserScopesResponse(BaseModel):
    """Response showing user's scope information"""
    username: str
    available_scopes: List[str]
    current_token_scopes: List[str] = []


# Environment Variable Models
class EnvVarCreate(BaseModel):
    """Request to create/update an environment variable"""
    name: str
    value: str

class EnvVarResponse(BaseModel):
    """Response for an environment variable"""
    name: str
    value: str
    created_at: str
    updated_at: str

class EnvVarListResponse(BaseModel):
    """Response for listing environment variables"""
    variables: List[EnvVarResponse]
    total_count: int
