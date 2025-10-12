"""Nessie API mock service for Capital One integration demo."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)

# Mock accounts
DEMO_ACCOUNTS = [
    {
        "account_id": "nessie_demo_001",
        "customer_id": "demo_customer",
        "type": "Credit Card",
        "nickname": "Capital One Venture Card",
        "balance": 2500.00,
        "currency": "USD",
    },
    {
        "account_id": "nessie_demo_002",
        "customer_id": "demo_customer",
        "type": "Checking",
        "nickname": "360 Checking",
        "balance": 5000.00,
        "currency": "USD",
    },
]

# Mock transactions
DEMO_TRANSACTIONS = [
    {
        "transaction_id": "txn_001",
        "account_id": "nessie_demo_001",
        "merchant": "tricky-sub.example",
        "amount": 49.99,
        "currency": "USD",
        "date": (datetime.now() - timedelta(days=5)).isoformat(),
        "description": "Subscription charge with hidden fees",
    },
    {
        "transaction_id": "txn_002",
        "account_id": "nessie_demo_001",
        "merchant": "clean-shop.example",
        "amount": 25.00,
        "currency": "USD",
        "date": (datetime.now() - timedelta(days=2)).isoformat(),
        "description": "Regular purchase",
    },
]


def get_accounts() -> List[Dict]:
    """Get mock accounts.

    Returns:
        List of demo accounts
    """
    logger.info("Nessie mock: Fetching accounts")
    return DEMO_ACCOUNTS


def get_transactions(account_id: str = None) -> List[Dict]:
    """Get mock transactions.

    Args:
        account_id: Optional account ID filter

    Returns:
        List of demo transactions
    """
    logger.info(f"Nessie mock: Fetching transactions for account {account_id}")
    if account_id:
        return [txn for txn in DEMO_TRANSACTIONS if txn["account_id"] == account_id]
    return DEMO_TRANSACTIONS


def submit_dispute(account_id: str, transaction_id: str, reason: str) -> Dict:
    """Submit a mock dispute.

    Args:
        account_id: Account ID
        transaction_id: Transaction ID
        reason: Dispute reason

    Returns:
        Mock dispute submission result
    """
    logger.info(f"Nessie mock: Submitting dispute for transaction {transaction_id}")

    return {
        "dispute_id": f"dispute_{transaction_id}",
        "status": "SUBMITTED",
        "transaction_id": transaction_id,
        "account_id": account_id,
        "reason": reason,
        "submitted_at": datetime.now().isoformat(),
        "estimated_resolution_days": 30,
        "provisional_credit": True,
    }


def post_refund(account_id: str, amount: float, merchant: str) -> Dict:
    """Post a mock refund.

    Args:
        account_id: Account ID
        amount: Refund amount
        merchant: Merchant name

    Returns:
        Mock refund result
    """
    logger.info(f"Nessie mock: Posting refund of ${amount} to account {account_id}")

    return {
        "refund_id": f"refund_{datetime.now().timestamp()}",
        "account_id": account_id,
        "amount": amount,
        "merchant": merchant,
        "status": "COMPLETED",
        "posted_at": datetime.now().isoformat(),
    }

