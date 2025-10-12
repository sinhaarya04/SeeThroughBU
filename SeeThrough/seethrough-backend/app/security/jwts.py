"""JWT token utilities."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from app.config import get_settings

settings = get_settings()


def create_access_token(user_id: int) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_min)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_alg)


def create_refresh_token(user_id: int) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_min)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_alg)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify an access token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_alg])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and verify a refresh token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_alg])
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.PyJWTError:
        return None

