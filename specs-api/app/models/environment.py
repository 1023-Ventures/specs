from pydantic import BaseModel
from typing import List


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
