"""Payment routes."""

import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.deps import CurrentUser, DBSession
from app.models.transaction import Transaction
from app.schemas.transaction import AuthorizeRequest, AuthorizeResponse, TransactionOut
from app.services.payments import authorize, settle

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/authorize", response_model=AuthorizeResponse, status_code=status.HTTP_201_CREATED)
def authorize_payment(data: AuthorizeRequest, db: DBSession, user: CurrentUser):
    """Authorize a payment transaction."""
    transaction = authorize(
        db=db,
        user=user,
        merchant_domain=data.merchant_domain,
        amount=data.amount,
        virtual_card_id=data.virtual_card_id,
    )

    meta = json.loads(transaction.meta_json)
    message = meta.get("decline_reason") if transaction.status.value == "DECLINED" else None

    return AuthorizeResponse(
        transaction_id=transaction.id,
        status=transaction.status.value,
        message=message,
    )


@router.post("/{transaction_id}/settle", response_model=TransactionOut)
def settle_transaction(transaction_id: int, db: DBSession, user: CurrentUser):
    """Settle an authorized transaction."""
    try:
        transaction = settle(db, transaction_id)

        # Verify ownership
        if transaction.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to settle this transaction",
            )

        meta = json.loads(transaction.meta_json)

        return TransactionOut(
            id=transaction.id,
            user_id=transaction.user_id,
            virtual_card_id=transaction.virtual_card_id,
            merchant_domain=transaction.merchant_domain,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status.value,
            meta=meta,
            created_at=transaction.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/transactions", response_model=List[TransactionOut])
def list_transactions(
    db: DBSession,
    user: CurrentUser,
    merchant_domain: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
):
    """List transactions for the current user."""
    query = db.query(Transaction).filter(Transaction.user_id == user.id)

    if merchant_domain:
        query = query.filter(Transaction.merchant_domain == merchant_domain)

    transactions = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for txn in transactions:
        meta = json.loads(txn.meta_json)
        result.append(
            TransactionOut(
                id=txn.id,
                user_id=txn.user_id,
                virtual_card_id=txn.virtual_card_id,
                merchant_domain=txn.merchant_domain,
                amount=txn.amount,
                currency=txn.currency,
                status=txn.status.value,
                meta=meta,
                created_at=txn.created_at,
            )
        )

    return result

