from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    # Alphanumeric + underscore only; 3–50 chars
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    # Accepts either an email address or a username
    login: str = Field(min_length=1)
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Safe public representation of a user. Never includes password_hash."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    favorite_club: Optional[str]
    favorite_league: Optional[str]
    is_active: bool
    created_at: datetime
