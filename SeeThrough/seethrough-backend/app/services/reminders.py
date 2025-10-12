"""Reminder service for subscription cancellation."""

import logging
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger(__name__)


def schedule_cancel_reminder(merchant_domain: str, trial_days: int, user_email: str) -> Dict:
    """Schedule a cancellation reminder.

    Args:
        merchant_domain: Merchant domain
        trial_days: Number of trial days
        user_email: User email for reminder

    Returns:
        Reminder details
    """
    cancel_date = datetime.now() + timedelta(days=trial_days - 1)

    logger.info(
        f"Scheduling cancel reminder for {user_email} - "
        f"{merchant_domain} trial ends in {trial_days} days"
    )

    # In a real implementation, this would:
    # 1. Store reminder in database
    # 2. Schedule background job
    # 3. Send calendar invite

    return {
        "reminder_id": f"reminder_{merchant_domain}_{int(datetime.now().timestamp())}",
        "merchant_domain": merchant_domain,
        "user_email": user_email,
        "cancel_date": cancel_date.isoformat(),
        "trial_days": trial_days,
        "calendar_link": f"webcal://example.com/reminder.ics",
        "status": "SCHEDULED",
    }


def generate_cancel_email_body(merchant_domain: str, order_id: str = None) -> str:
    """Generate cancellation email body.

    Args:
        merchant_domain: Merchant domain
        order_id: Optional order ID

    Returns:
        Email body text
    """
    email_body = f"""
Dear {merchant_domain} Support,

I would like to cancel my subscription/trial before any charges are applied.

"""

    if order_id:
        email_body += f"Order ID: {order_id}\n"

    email_body += """
Please confirm the cancellation and ensure no further charges will be made.

Thank you for your assistance.

Best regards
"""

    return email_body.strip()

