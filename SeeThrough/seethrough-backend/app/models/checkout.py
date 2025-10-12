"""Checkout model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base
from app.utils.time import now_utc


class Checkout(Base):
    """Checkout session model."""

    __tablename__ = "checkouts"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)

    # Relationships
    merchant = relationship("Merchant", backref="checkouts")

    def __repr__(self):
        return f"<Checkout(id={self.id}, merchant_id={self.merchant_id}, url={self.url})>"

