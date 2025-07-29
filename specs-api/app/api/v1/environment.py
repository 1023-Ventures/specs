from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...services.env_service import EnvironmentService
from ...services.auth_service import AuthService
from ...models.environment import EnvVarCreate

router = APIRouter()
security = HTTPBearer()
env_service = EnvironmentService()
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from JWT token"""
    return auth_service.get_current_user_from_token(credentials)


# Environment Variables endpoints
@router.get("/")
async def get_user_env_vars(current_user: dict = Depends(get_current_user)):
    """Get all environment variables for the current user"""
    return env_service.get_user_env_vars(current_user)


@router.get("/{name}")
async def get_user_env_var(name: str, current_user: dict = Depends(get_current_user)):
    """Get a specific environment variable for the current user"""
    return env_service.get_user_env_var(name, current_user)


@router.post("/")
async def create_or_update_env_var(
    env_var: EnvVarCreate, 
    current_user: dict = Depends(get_current_user)
):
    """Create or update an environment variable for the current user"""
    return env_service.set_user_env_var(env_var.name, env_var.value, current_user)


@router.put("/{name}")
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
    return env_service.set_user_env_var(env_var.name, env_var.value, current_user)


@router.delete("/{name}")
async def delete_env_var(name: str, current_user: dict = Depends(get_current_user)):
    """Delete an environment variable for the current user"""
    return env_service.delete_user_env_var(name, current_user)
