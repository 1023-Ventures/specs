from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...services.auth_service import AuthService
from ...models.auth import UserCreate, UserResponse, Token, UserLogin, EnvVarCreate
from ...core.security import require_scopes, check_scope_access

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


@router.get("/")
async def root():
    """Health check endpoint"""
    return auth_service.get_health_status()


@router.get("/scopes")
async def get_available_scopes():
    """Get all available scopes in the system"""
    return auth_service.get_available_scopes()


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user"""
    return auth_service.register_user(user)


@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Login user and return JWT token with requested scopes"""
    return auth_service.login_user(user_credentials)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from JWT token"""
    return auth_service.get_current_user_from_token(credentials)


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile (requires read_profile scope)"""
    if not check_scope_access(current_user, "read_profile"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: read_profile"
        )
    return auth_service.get_user_profile(current_user)


@router.put("/profile")
async def update_user_profile(current_user: dict = Depends(get_current_user)):
    """Update user profile (requires write_profile scope)"""
    if not check_scope_access(current_user, "write_profile"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: write_profile"
        )
    return {"message": f"Profile updated for {current_user['username']}"}


@router.get("/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (requires read_users scope)"""
    if not check_scope_access(current_user, "read_users"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: read_users"
        )
    return {"message": "Here are all users", "requested_by": current_user['username']}


@router.get("/admin")
async def admin_endpoint(current_user: dict = Depends(get_current_user)):
    """Admin-only endpoint (requires admin scope)"""
    if not check_scope_access(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: admin"
        )
    return {"message": "Welcome to admin area!", "admin": current_user['username']}


@router.get("/me/scopes")
async def get_my_scopes(current_user: dict = Depends(get_current_user)):
    """Get current user's scope information"""
    return auth_service.get_user_scopes(current_user)


@router.get("/users/{user_id}/scopes")
async def get_user_scopes_by_id(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get a user's available scopes (admin only)"""
    if not check_scope_access(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: admin"
        )
    
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user["id"],
        "username": user["username"],
        "available_scopes": user["available_scopes"]
    }


@router.post("/users/{user_id}/scopes/{scope}")
async def grant_scope_to_user(
    user_id: int, 
    scope: str, 
    current_user: dict = Depends(get_current_user)
):
    """Grant a scope to a user (admin only)"""
    if not check_scope_access(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: admin"
        )
    
    if auth_service.grant_scope_to_user(user_id, scope, current_user["username"]):
        return {"message": f"Scope '{scope}' granted to user {user_id}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to grant scope. Invalid scope or user not found."
        )


@router.delete("/users/{user_id}/scopes/{scope}")
async def revoke_scope_from_user(
    user_id: int, 
    scope: str, 
    current_user: dict = Depends(get_current_user)
):
    """Revoke a scope from a user (admin only)"""
    if not check_scope_access(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: admin"
        )
    
    if auth_service.revoke_scope_from_user(user_id, scope):
        return {"message": f"Scope '{scope}' revoked from user {user_id}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to revoke scope."
        )


@router.get("/users/scopes")
async def list_all_users_with_scopes(current_user: dict = Depends(get_current_user)):
    """List all users with their scopes (admin only)"""
    if not check_scope_access(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Required scope: admin"
        )
    
    return auth_service.list_all_users_with_scopes()


@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Example protected route (no specific scope required)"""
    return auth_service.get_protected_message(current_user)


# Environment Variables endpoints
@router.get("/environment-variables")
async def get_user_env_vars(current_user: dict = Depends(get_current_user)):
    """Get all environment variables for the current user"""
    return auth_service.get_user_env_vars(current_user)


@router.get("/environment-variables/{name}")
async def get_user_env_var(name: str, current_user: dict = Depends(get_current_user)):
    """Get a specific environment variable for the current user"""
    return auth_service.get_user_env_var(name, current_user)


@router.post("/environment-variables")
async def create_or_update_env_var(
    env_var: EnvVarCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Create or update an environment variable for the current user"""
    return auth_service.set_user_env_var(env_var.name, env_var.value, current_user)


@router.put("/environment-variables/{name}")
async def update_env_var(
    name: str,
    env_var: EnvVarCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update an environment variable for the current user"""
    # Ensure the name in the URL matches the name in the body
    if name != env_var.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Environment variable name in URL must match name in request body"
        )
    return auth_service.set_user_env_var(env_var.name, env_var.value, current_user)


@router.delete("/environment-variables/{name}")
async def delete_env_var(name: str, current_user: dict = Depends(get_current_user)):
    """Delete an environment variable for the current user"""
    return auth_service.delete_user_env_var(name, current_user)
