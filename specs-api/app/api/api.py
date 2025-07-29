from fastapi import APIRouter
from .v1 import auth, environment

api_router = APIRouter()

# Include all v1 routes
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(environment.router, prefix="/environment-variables", tags=["environment"])
