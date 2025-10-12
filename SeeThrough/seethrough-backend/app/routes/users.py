"""User routes."""

from fastapi import APIRouter

from app.deps import CurrentUser
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_current_user(user: CurrentUser):
    """Get current user profile."""
    return user

