"""Merchant model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db import Base
from app.utils.time import now_utc


class Merchant(Base):
    """Merchant model."""

    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)

    def __repr__(self):
        return f"<Merchant(id={self.id}, domain={self.domain}, risk_score={self.risk_score})>"

