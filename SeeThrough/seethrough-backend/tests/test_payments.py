"""Tests for payment endpoints."""

from datetime import datetime, timedelta

import pytest


def test_authorize_payment_within_limit(client, auth_headers):
    """Test authorizing payment within card limit."""
    # Create a virtual card
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    card_response = client.post(
        "/virtual-cards/",
        json={
            "merchant_domain": "shop.example",
            "max_amount": 100.0,
            "expires_at": expires_at,
            "merchant_lock": True,
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Authorize payment within limit
    response = client.post(
        "/payments/authorize",
        json={
            "merchant_domain": "shop.example",
            "amount": 50.0,
            "virtual_card_id": card_id,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "AUTHORIZED"
    assert "transaction_id" in data


def test_authorize_payment_over_limit(client, auth_headers):
    """Test authorizing payment over card limit is declined."""
    # Create a virtual card with low limit
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    card_response = client.post(
        "/virtual-cards/",
        json={
            "merchant_domain": "shop.example",
            "max_amount": 50.0,
            "expires_at": expires_at,
            "merchant_lock": True,
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Try to authorize payment over limit
    response = client.post(
        "/payments/authorize",
        json={
            "merchant_domain": "shop.example",
            "amount": 100.0,
            "virtual_card_id": card_id,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "DECLINED"
    assert "limit" in data["message"].lower()


def test_authorize_payment_wrong_merchant(client, auth_headers):
    """Test payment to wrong merchant is declined when card is merchant-locked."""
    # Create a virtual card locked to specific merchant
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    card_response = client.post(
        "/virtual-cards/",
        json={
            "merchant_domain": "shop-a.example",
            "max_amount": 100.0,
            "expires_at": expires_at,
            "merchant_lock": True,
        },
        headers=auth_headers,
    )
    card_id = card_response.json()["id"]

    # Try to use card at different merchant
    response = client.post(
        "/payments/authorize",
        json={
            "merchant_domain": "shop-b.example",
            "amount": 50.0,
            "virtual_card_id": card_id,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "DECLINED"


def test_authorize_payment_without_card(client, auth_headers):
    """Test authorizing payment without virtual card."""
    response = client.post(
        "/payments/authorize",
        json={
            "merchant_domain": "shop.example",
            "amount": 25.0,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "AUTHORIZED"


def test_list_transactions(client, auth_headers):
    """Test listing transactions."""
    # Create a few transactions
    for i in range(3):
        client.post(
            "/payments/authorize",
            json={
                "merchant_domain": f"shop-{i}.example",
                "amount": 10.0 + i,
            },
            headers=auth_headers,
        )

    # List transactions
    response = client.get("/payments/transactions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

