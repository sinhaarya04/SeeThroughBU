"""Payment authorization service."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionStatus
from app.models.user import User
from app.models.virtual_card import VirtualCard, VirtualCardStatus

logger = logging.getLogger(__name__)


def authorize(
    db: Session,
    user: User,
    merchant_domain: str,
    amount: float,
    virtual_card_id: int = None,
    currency: str = "USD",
) -> Transaction:
    """Authorize a payment transaction.

    Args:
        db: Database session
        user: User making the payment
        merchant_domain: Merchant domain
        amount: Transaction amount
        virtual_card_id: Optional virtual card ID
        currency: Currency code

    Returns:
        Created Transaction instance
    """
    status = TransactionStatus.AUTHORIZED
    decline_reason = None

    # If virtual card is specified, enforce controls
    if virtual_card_id:
        card = (
            db.query(VirtualCard)
            .filter(VirtualCard.id == virtual_card_id, VirtualCard.user_id == user.id)
            .first()
        )

        if not card:
            status = TransactionStatus.DECLINED
            decline_reason = "Virtual card not found"
            logger.warning(f"Card {virtual_card_id} not found for user {user.id}")

        elif card.status != VirtualCardStatus.ACTIVE:
            status = TransactionStatus.DECLINED
            decline_reason = f"Card is {card.status.value}"
            logger.warning(f"Card {virtual_card_id} is {card.status.value}")

        elif (card.expires_at.replace(tzinfo=timezone.utc) if card.expires_at.tzinfo is None else card.expires_at) < datetime.now(timezone.utc):
            status = TransactionStatus.DECLINED
            decline_reason = "Card expired"
            logger.warning(f"Card {virtual_card_id} expired")

        elif amount > card.max_amount:
            status = TransactionStatus.DECLINED
            decline_reason = f"Amount ${amount} exceeds card limit ${card.max_amount}"
            logger.warning(f"Amount ${amount} exceeds card limit ${card.max_amount}")

        else:
            # Check merchant lock
            controls = json.loads(card.controls_json)
            if controls.get("merchant_lock") and card.merchant_domain != merchant_domain:
                status = TransactionStatus.DECLINED
                decline_reason = (
                    f"Card locked to {card.merchant_domain}, attempted {merchant_domain}"
                )
                logger.warning(decline_reason)

    # Create transaction
    meta = {
        "decline_reason": decline_reason,
        "virtual_card_used": virtual_card_id is not None,
    }

    transaction = Transaction(
        user_id=user.id,
        virtual_card_id=virtual_card_id,
        merchant_domain=merchant_domain,
        amount=amount,
        currency=currency,
        status=status,
        meta_json=json.dumps(meta),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    logger.info(
        f"Transaction {transaction.id}: ${amount} to {merchant_domain} - {status.value}"
    )

    return transaction


def settle(db: Session, transaction_id: int) -> Transaction:
    """Settle an authorized transaction.

    Args:
        db: Database session
        transaction_id: Transaction ID

    Returns:
        Updated Transaction instance
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise ValueError("Transaction not found")

    if transaction.status != TransactionStatus.AUTHORIZED:
        raise ValueError(f"Cannot settle transaction with status {transaction.status.value}")

    transaction.status = TransactionStatus.SETTLED
    db.commit()
    db.refresh(transaction)

    logger.info(f"Settled transaction {transaction_id}")
    return transaction

