"""Authentication service."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.security.password import hash_password, verify_password


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(db: Session, email: str, password: str) -> User:
    """Create a new user."""
    hashed_password = hash_password(password)
    user = User(email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

