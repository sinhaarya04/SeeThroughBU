"""Risk event model."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base
from app.utils.time import now_utc


class RiskEventKind(str, enum.Enum):
    """Risk event types."""

    HIDDEN_FEE = "HIDDEN_FEE"
    TRIAL_AUTORENEW = "TRIAL_AUTORENEW"
    PRECHECKED_ADDON = "PRECHECKED_ADDON"
    LOOKALIKE_DOMAIN = "LOOKALIKE_DOMAIN"


class RiskEvent(Base):
    """Risk event model - detected dark patterns."""

    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True)
    checkout_id = Column(Integer, ForeignKey("checkouts.id"), nullable=False)
    kind = Column(Enum(RiskEventKind), nullable=False, index=True)
    detail_json = Column(String, nullable=False)  # JSON string
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)

    # Relationships
    checkout = relationship("Checkout", backref="risk_events")

    def __repr__(self):
        return f"<RiskEvent(id={self.id}, kind={self.kind}, score={self.score})>"

