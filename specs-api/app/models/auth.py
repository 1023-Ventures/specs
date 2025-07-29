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
