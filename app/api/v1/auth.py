from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...services.auth_service import AuthService
from ...models.auth import UserCreate, UserResponse, Token, UserLogin

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


@router.get("/")
async def root():
    """Health check endpoint"""
    return auth_service.get_health_status()


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user"""
    return auth_service.register_user(user)


@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Login user and return JWT token"""
    return auth_service.login_user(user_credentials)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from JWT token"""
    return auth_service.get_current_user_from_token(credentials)


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile (protected route)"""
    return auth_service.get_user_profile(current_user)


@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Example protected route"""
    return auth_service.get_protected_message(current_user)
