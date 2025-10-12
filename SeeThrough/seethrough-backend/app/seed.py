"""Seed script for demo data."""

import sys

from app.db import SessionLocal
from app.models.merchant import Merchant
from app.models.user import User
from app.security.password import hash_password


def seed_database():
    """Seed the database with demo data."""
    db = SessionLocal()

    try:
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == "demo@stc.app").first()
        if not demo_user:
            demo_user = User(
                email="demo@stc.app",
                password_hash=hash_password("demo1234"),
            )
            db.add(demo_user)
            print("✓ Created demo user: demo@stc.app / demo1234")
        else:
            print("→ Demo user already exists")

        # Check if demo merchants exist
        tricky_merchant = (
            db.query(Merchant).filter(Merchant.domain == "tricky-sub.example").first()
        )
        if not tricky_merchant:
            tricky_merchant = Merchant(
                domain="tricky-sub.example",
                display_name="Tricky Subscription Service",
                risk_score=78.0,
            )
            db.add(tricky_merchant)
            print("✓ Created merchant: tricky-sub.example")
        else:
            print("→ Merchant tricky-sub.example already exists")

        clean_merchant = (
            db.query(Merchant).filter(Merchant.domain == "clean-shop.example").first()
        )
        if not clean_merchant:
            clean_merchant = Merchant(
                domain="clean-shop.example",
                display_name="Clean Shop",
                risk_score=5.0,
            )
            db.add(clean_merchant)
            print("✓ Created merchant: clean-shop.example")
        else:
            print("→ Merchant clean-shop.example already exists")

        db.commit()
        print("\n✅ Database seeded successfully!")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

