"""User model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db import Base
from app.utils.time import now_utc


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

