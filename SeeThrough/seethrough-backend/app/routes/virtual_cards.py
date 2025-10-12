"""Virtual card routes."""

import json
from typing import List

from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, DBSession
from app.models.virtual_card import VirtualCard
from app.schemas.virtual_card import VirtualCardCreate, VirtualCardOut
from app.services.virtual_card import close_card, create_virtual_card, freeze_card

router = APIRouter(prefix="/virtual-cards", tags=["Virtual Cards"])


@router.post("/", response_model=VirtualCardOut, status_code=status.HTTP_201_CREATED)
def create_card(data: VirtualCardCreate, db: DBSession, user: CurrentUser):
    """Create a new virtual card."""
    card = create_virtual_card(
        db=db,
        user_id=user.id,
        merchant_domain=data.merchant_domain,
        max_amount=data.max_amount,
        expires_at=data.expires_at,
        merchant_lock=data.merchant_lock,
    )

    # Parse controls for response
    controls = json.loads(card.controls_json)

    return VirtualCardOut(
        id=card.id,
        user_id=card.user_id,
        merchant_domain=card.merchant_domain,
        pan_last4=card.pan_last4,
        alias_token=card.alias_token,
        max_amount=card.max_amount,
        currency=card.currency,
        expires_at=card.expires_at,
        status=card.status.value,
        controls=controls,
        created_at=card.created_at,
    )


@router.post("/{card_id}/freeze", response_model=VirtualCardOut)
def freeze_virtual_card(card_id: int, db: DBSession, user: CurrentUser):
    """Freeze a virtual card."""
    try:
        card = freeze_card(db, card_id, user.id)
        controls = json.loads(card.controls_json)

        return VirtualCardOut(
            id=card.id,
            user_id=card.user_id,
            merchant_domain=card.merchant_domain,
            pan_last4=card.pan_last4,
            alias_token=card.alias_token,
            max_amount=card.max_amount,
            currency=card.currency,
            expires_at=card.expires_at,
            status=card.status.value,
            controls=controls,
            created_at=card.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{card_id}/close", response_model=VirtualCardOut)
def close_virtual_card(card_id: int, db: DBSession, user: CurrentUser):
    """Close a virtual card."""
    try:
        card = close_card(db, card_id, user.id)
        controls = json.loads(card.controls_json)

        return VirtualCardOut(
            id=card.id,
            user_id=card.user_id,
            merchant_domain=card.merchant_domain,
            pan_last4=card.pan_last4,
            alias_token=card.alias_token,
            max_amount=card.max_amount,
            currency=card.currency,
            expires_at=card.expires_at,
            status=card.status.value,
            controls=controls,
            created_at=card.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/", response_model=List[VirtualCardOut])
def list_cards(db: DBSession, user: CurrentUser):
    """List all virtual cards for the current user."""
    cards = db.query(VirtualCard).filter(VirtualCard.user_id == user.id).all()

    result = []
    for card in cards:
        controls = json.loads(card.controls_json)
        result.append(
            VirtualCardOut(
                id=card.id,
                user_id=card.user_id,
                merchant_domain=card.merchant_domain,
                pan_last4=card.pan_last4,
                alias_token=card.alias_token,
                max_amount=card.max_amount,
                currency=card.currency,
                expires_at=card.expires_at,
                status=card.status.value,
                controls=controls,
                created_at=card.created_at,
            )
        )

    return result

