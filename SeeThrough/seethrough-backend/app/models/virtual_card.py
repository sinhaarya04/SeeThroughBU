"""Virtual card model."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base
from app.utils.time import now_utc


class VirtualCardStatus(str, enum.Enum):
    """Virtual card status."""

    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class VirtualCard(Base):
    """Virtual card model."""

    __tablename__ = "virtual_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_domain = Column(String, nullable=False)
    pan_last4 = Column(String(4), nullable=False)
    alias_token = Column(String, unique=True, nullable=False, index=True)
    max_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    expires_at = Column(DateTime, nullable=False)
    status = Column(Enum(VirtualCardStatus), default=VirtualCardStatus.ACTIVE, nullable=False)
    controls_json = Column(String, nullable=False)  # JSON string
    created_at = Column(DateTime, default=now_utc, nullable=False)

    # Relationships
    user = relationship("User", backref="virtual_cards")

    def __repr__(self):
        return (
            f"<VirtualCard(id={self.id}, user_id={self.user_id}, "
            f"merchant={self.merchant_domain}, status={self.status})>"
        )

