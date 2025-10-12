"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status

from app.deps import DBSession
from app.schemas.user import (
    AccessTokenResponse,
    RefreshRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.security.auth import authenticate_user, create_user
from app.security.jwts import create_access_token, create_refresh_token, decode_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: DBSession):
    """Register a new user."""
    # Check if user exists
    from app.models.user import User

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = create_user(db, data.email, data.password)

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: DBSession):
    """Login with email and password."""
    user = authenticate_user(db, data.email, data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshRequest, db: DBSession):
    """Refresh access token."""
    payload = decode_refresh_token(data.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Verify user exists
    from app.models.user import User

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Generate new access token
    access_token = create_access_token(user.id)

    return AccessTokenResponse(access_token=access_token)

