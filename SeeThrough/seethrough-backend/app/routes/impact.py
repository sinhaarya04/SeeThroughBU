"""Impact and summary routes."""

from fastapi import APIRouter
from sqlalchemy import func

from app.deps import CurrentUser, DBSession
from app.models.dispute import Dispute
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.transaction import Transaction, TransactionStatus

router = APIRouter(prefix="/impact", tags=["Impact"])


@router.get("/summary")
def get_impact_summary(db: DBSession, user: CurrentUser):
    """Get user impact summary."""
    # Count declined transactions (blocked)
    declined_count = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.user_id == user.id, Transaction.status == TransactionStatus.DECLINED)
        .scalar()
    )

    # Sum of declined amounts (potential savings)
    declined_total = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == user.id, Transaction.status == TransactionStatus.DECLINED)
        .scalar()
        or 0.0
    )

    # Count paused/cancelled subscriptions
    paused_subs = (
        db.query(func.count(Subscription.id))
        .filter(
            Subscription.user_id == user.id,
            Subscription.status.in_([SubscriptionStatus.PAUSED, SubscriptionStatus.CANCELLED]),
        )
        .scalar()
    )

    # Count filed disputes
    disputes_filed = (
        db.query(func.count(Dispute.id)).filter(Dispute.user_id == user.id).scalar()
    )

    return {
        "blocked_transactions": declined_count,
        "fees_blocked_usd": round(declined_total, 2),
        "subscriptions_paused": paused_subs,
        "disputes_filed": disputes_filed,
        "estimated_savings_usd": round(declined_total, 2),
    }

