"""Capture model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base
from app.utils.time import now_utc


class Capture(Base):
    """Capture model - stores screenshots and HTML snapshots."""

    __tablename__ = "captures"

    id = Column(Integer, primary_key=True, index=True)
    checkout_id = Column(Integer, ForeignKey("checkouts.id"), nullable=False)
    image_url = Column(String, nullable=True)
    html_snapshot_url = Column(String, nullable=True)
    sha256 = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=now_utc, nullable=False)

    # Relationships
    checkout = relationship("Checkout", backref="captures")

    def __repr__(self):
        return f"<Capture(id={self.id}, checkout_id={self.checkout_id}, sha256={self.sha256[:8]})>"

