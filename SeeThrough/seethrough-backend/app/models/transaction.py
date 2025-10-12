"""Transaction model."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base
from app.utils.time import now_utc


class TransactionStatus(str, enum.Enum):
    """Transaction status."""

    AUTHORIZED = "AUTHORIZED"
    SETTLED = "SETTLED"
    DECLINED = "DECLINED"


class Transaction(Base):
    """Transaction model."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    virtual_card_id = Column(Integer, ForeignKey("virtual_cards.id"), nullable=True)
    merchant_domain = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(
        Enum(TransactionStatus), default=TransactionStatus.AUTHORIZED, nullable=False
    )
    meta_json = Column(String, nullable=False)  # JSON string
    created_at = Column(DateTime, default=now_utc, nullable=False)

    # Relationships
    user = relationship("User", backref="transactions")
    virtual_card = relationship("VirtualCard", backref="transactions")

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, status={self.status})>"
        )

