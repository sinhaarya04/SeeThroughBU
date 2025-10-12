"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    """Access token response."""

    access_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class UserOut(BaseModel):
    """User output schema."""

    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

