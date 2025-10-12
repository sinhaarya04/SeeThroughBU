"""Tests for virtual card endpoints."""

from datetime import datetime, timedelta

import pytest


def test_create_virtual_card(client, auth_headers):
    """Test creating a virtual card."""
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()

    response = client.post(
        "/virtual-cards/",
        json={
            "merchant_domain": "test-merchant.example",
            "max_amount": 100.0,
            "expires_at": expires_at,
            "merchant_lock": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["merchant_domain"] == "test-merchant.example"
    assert data["max_amount"] == 100.0
    assert data["status"] == "ACTIVE"
    assert "pan_last4" in data
    assert "alias_token" in data
    assert data["controls"]["merchant_lock"] is True


def test_freeze_virtual_card(client, auth_headers):
    """Test freezing a virtual card."""
    # Create a card first
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    create_response = client.post(
        "/virtual-cards/",
        json={
            "merchant_domain": "test-merchant.example",
            "max_amount": 50.0,
            "expires_at": expires_at,
            "merchant_lock": True,
        },
        headers=auth_headers,
    )
    card_id = create_response.json()["id"]

    # Freeze the card
    response = client.post(f"/virtual-cards/{card_id}/freeze", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FROZEN"


def test_close_virtual_card(client, auth_headers):
    """Test closing a virtual card."""
    # Create a card first
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()
    create_response = client.post(
        "/virtual-cards/",
        json={
            "merchant_domain": "test-merchant.example",
            "max_amount": 50.0,
            "expires_at": expires_at,
            "merchant_lock": True,
        },
        headers=auth_headers,
    )
    card_id = create_response.json()["id"]

    # Close the card
    response = client.post(f"/virtual-cards/{card_id}/close", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CLOSED"


def test_list_virtual_cards(client, auth_headers):
    """Test listing virtual cards."""
    # Create a few cards
    expires_at = (datetime.now() + timedelta(days=30)).isoformat()

    for i in range(3):
        client.post(
            "/virtual-cards/",
            json={
                "merchant_domain": f"merchant-{i}.example",
                "max_amount": 100.0 + i * 10,
                "expires_at": expires_at,
                "merchant_lock": True,
            },
            headers=auth_headers,
        )

    # List cards
    response = client.get("/virtual-cards/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

