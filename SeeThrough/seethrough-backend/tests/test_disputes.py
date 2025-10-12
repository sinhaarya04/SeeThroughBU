"""Tests for dispute endpoints."""

import pytest


def test_create_dispute(client, auth_headers):
    """Test creating a dispute."""
    # First create a transaction
    txn_response = client.post(
        "/payments/authorize",
        json={
            "merchant_domain": "shady-shop.example",
            "amount": 99.99,
        },
        headers=auth_headers,
    )
    transaction_id = txn_response.json()["transaction_id"]

    # Create a dispute
    response = client.post(
        "/disputes/",
        json={
            "transaction_id": transaction_id,
            "reason": "Hidden fees were not disclosed during checkout",
            "capture_ids": [],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["transaction_id"] == transaction_id
    assert data["reason"] == "Hidden fees were not disclosed during checkout"
    assert data["status"] == "DRAFT"
    assert "letter_pdf_url" in data


def test_list_disputes(client, auth_headers):
    """Test listing disputes."""
    # Create a transaction and dispute
    txn_response = client.post(
        "/payments/authorize",
        json={
            "merchant_domain": "shop.example",
            "amount": 50.0,
        },
        headers=auth_headers,
    )
    transaction_id = txn_response.json()["transaction_id"]

    client.post(
        "/disputes/",
        json={
            "transaction_id": transaction_id,
            "reason": "Test dispute",
            "capture_ids": [],
        },
        headers=auth_headers,
    )

    # List disputes
    response = client.get("/disputes/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_dispute(client, auth_headers):
    """Test getting a specific dispute."""
    # Create transaction and dispute
    txn_response = client.post(
        "/payments/authorize",
        json={
            "merchant_domain": "shop.example",
            "amount": 75.0,
        },
        headers=auth_headers,
    )
    transaction_id = txn_response.json()["transaction_id"]

    dispute_response = client.post(
        "/disputes/",
        json={
            "transaction_id": transaction_id,
            "reason": "Unauthorized charge",
            "capture_ids": [],
        },
        headers=auth_headers,
    )
    dispute_id = dispute_response.json()["id"]

    # Get the dispute
    response = client.get(f"/disputes/{dispute_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dispute_id
    assert data["reason"] == "Unauthorized charge"

