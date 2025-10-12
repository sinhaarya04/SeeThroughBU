"""Virtual card service."""

import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.virtual_card import VirtualCard, VirtualCardStatus
from app.utils.ids import generate_alias_token, generate_pan_last4

logger = logging.getLogger(__name__)


def create_virtual_card(
    db: Session,
    user_id: int,
    merchant_domain: str,
    max_amount: float,
    expires_at: datetime,
    merchant_lock: bool = True,
    currency: str = "USD",
) -> VirtualCard:
    """Create a new virtual card.

    Args:
        db: Database session
        user_id: User ID
        merchant_domain: Merchant domain to lock card to
        max_amount: Maximum spend amount
        expires_at: Expiration datetime
        merchant_lock: Whether to lock to specific merchant
        currency: Currency code

    Returns:
        Created VirtualCard instance
    """
    # Generate card details
    alias_token = generate_alias_token()
    pan_last4 = generate_pan_last4()

    # Build controls
    controls = {
        "merchant_lock": merchant_lock,
        "spend_cap": True,
        "auto_expire": True,
    }

    # Create card
    card = VirtualCard(
        user_id=user_id,
        merchant_domain=merchant_domain,
        pan_last4=pan_last4,
        alias_token=alias_token,
        max_amount=max_amount,
        currency=currency,
        expires_at=expires_at,
        status=VirtualCardStatus.ACTIVE,
        controls_json=json.dumps(controls),
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    logger.info(
        f"Created virtual card {card.id} for user {user_id}, "
        f"merchant {merchant_domain}, max ${max_amount}"
    )

    return card


def freeze_card(db: Session, card_id: int, user_id: int) -> VirtualCard:
    """Freeze a virtual card.

    Args:
        db: Database session
        card_id: Card ID
        user_id: User ID (for authorization)

    Returns:
        Updated VirtualCard instance
    """
    card = db.query(VirtualCard).filter(
        VirtualCard.id == card_id, VirtualCard.user_id == user_id
    ).first()

    if not card:
        raise ValueError("Card not found")

    card.status = VirtualCardStatus.FROZEN
    db.commit()
    db.refresh(card)

    logger.info(f"Froze virtual card {card_id}")
    return card


def close_card(db: Session, card_id: int, user_id: int) -> VirtualCard:
    """Close a virtual card.

    Args:
        db: Database session
        card_id: Card ID
        user_id: User ID (for authorization)

    Returns:
        Updated VirtualCard instance
    """
    card = db.query(VirtualCard).filter(
        VirtualCard.id == card_id, VirtualCard.user_id == user_id
    ).first()

    if not card:
        raise ValueError("Card not found")

    card.status = VirtualCardStatus.CLOSED
    db.commit()
    db.refresh(card)

    logger.info(f"Closed virtual card {card_id}")
    return card

