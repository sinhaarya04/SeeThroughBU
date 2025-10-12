"""Subscription model."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base
from app.utils.time import now_utc


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


class Subscription(Base):
    """Subscription tracking model."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    plan_name = Column(String, nullable=False)
    trial_days = Column(Integer, default=0, nullable=False)
    renew_every_days = Column(Integer, nullable=False)
    next_renew_ts = Column(DateTime, nullable=True)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)

    # Relationships
    user = relationship("User", backref="subscriptions")
    merchant = relationship("Merchant", backref="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status})>"

