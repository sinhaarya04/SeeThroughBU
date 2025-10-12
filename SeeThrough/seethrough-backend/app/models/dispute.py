"""Dispute model."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base
from app.utils.time import now_utc


class DisputeStatus(str, enum.Enum):
    """Dispute status."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    RESOLVED = "RESOLVED"


class Dispute(Base):
    """Dispute model."""

    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    reason = Column(Text, nullable=False)
    letter_pdf_url = Column(String, nullable=True)
    evidence_zip_url = Column(String, nullable=True)
    status = Column(Enum(DisputeStatus), default=DisputeStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=now_utc, nullable=False)

    # Relationships
    user = relationship("User", backref="disputes")
    transaction = relationship("Transaction", backref="disputes")

    def __repr__(self):
        return f"<Dispute(id={self.id}, user_id={self.user_id}, status={self.status})>"

