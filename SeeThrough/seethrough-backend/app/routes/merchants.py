"""Merchant routes."""

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, DBSession
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantOut

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.get("/{domain}", response_model=MerchantOut)
def get_merchant(domain: str, db: DBSession, user: CurrentUser):
    """Get merchant information by domain."""
    merchant = db.query(Merchant).filter(Merchant.domain == domain).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchant not found",
        )

    return merchant


@router.get("/", response_model=List[MerchantOut])
def list_merchants(db: DBSession, user: CurrentUser, skip: int = 0, limit: int = 100):
    """List all merchants."""
    merchants = db.query(Merchant).offset(skip).limit(limit).all()
    return merchants

