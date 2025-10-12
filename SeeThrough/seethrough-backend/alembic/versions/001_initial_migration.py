"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create merchants table
    op.create_table(
        'merchants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_merchants_domain'), 'merchants', ['domain'], unique=True)
    op.create_index(op.f('ix_merchants_id'), 'merchants', ['id'], unique=False)

    # Create checkouts table
    op.create_table(
        'checkouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('merchant_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkouts_id'), 'checkouts', ['id'], unique=False)

    # Create captures table
    op.create_table(
        'captures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('checkout_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('html_snapshot_url', sa.String(), nullable=True),
        sa.Column('sha256', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['checkout_id'], ['checkouts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_captures_id'), 'captures', ['id'], unique=False)
    op.create_index(op.f('ix_captures_sha256'), 'captures', ['sha256'], unique=False)

    # Create risk_events table
    op.create_table(
        'risk_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('checkout_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.Enum('HIDDEN_FEE', 'TRIAL_AUTORENEW', 'PRECHECKED_ADDON', 'LOOKALIKE_DOMAIN', name='riskeventkind'), nullable=False),
        sa.Column('detail_json', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['checkout_id'], ['checkouts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_events_id'), 'risk_events', ['id'], unique=False)
    op.create_index(op.f('ix_risk_events_kind'), 'risk_events', ['kind'], unique=False)

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('merchant_id', sa.Integer(), nullable=False),
        sa.Column('plan_name', sa.String(), nullable=False),
        sa.Column('trial_days', sa.Integer(), nullable=False),
        sa.Column('renew_every_days', sa.Integer(), nullable=False),
        sa.Column('next_renew_ts', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'PAUSED', 'CANCELLED', name='subscriptionstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['merchant_id'], ['merchants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)

    # Create virtual_cards table
    op.create_table(
        'virtual_cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('merchant_domain', sa.String(), nullable=False),
        sa.Column('pan_last4', sa.String(length=4), nullable=False),
        sa.Column('alias_token', sa.String(), nullable=False),
        sa.Column('max_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'FROZEN', 'CLOSED', name='virtualcardstatus'), nullable=False),
        sa.Column('controls_json', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_virtual_cards_alias_token'), 'virtual_cards', ['alias_token'], unique=True)
    op.create_index(op.f('ix_virtual_cards_id'), 'virtual_cards', ['id'], unique=False)

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('virtual_card_id', sa.Integer(), nullable=True),
        sa.Column('merchant_domain', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.Enum('AUTHORIZED', 'SETTLED', 'DECLINED', name='transactionstatus'), nullable=False),
        sa.Column('meta_json', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['virtual_card_id'], ['virtual_cards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_merchant_domain'), 'transactions', ['merchant_domain'], unique=False)

    # Create disputes table
    op.create_table(
        'disputes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('letter_pdf_url', sa.String(), nullable=True),
        sa.Column('evidence_zip_url', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'RESOLVED', name='disputestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_disputes_id'), 'disputes', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_disputes_id'), table_name='disputes')
    op.drop_table('disputes')
    op.drop_index(op.f('ix_transactions_merchant_domain'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_virtual_cards_id'), table_name='virtual_cards')
    op.drop_index(op.f('ix_virtual_cards_alias_token'), table_name='virtual_cards')
    op.drop_table('virtual_cards')
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_risk_events_kind'), table_name='risk_events')
    op.drop_index(op.f('ix_risk_events_id'), table_name='risk_events')
    op.drop_table('risk_events')
    op.drop_index(op.f('ix_captures_sha256'), table_name='captures')
    op.drop_index(op.f('ix_captures_id'), table_name='captures')
    op.drop_table('captures')
    op.drop_index(op.f('ix_checkouts_id'), table_name='checkouts')
    op.drop_table('checkouts')
    op.drop_index(op.f('ix_merchants_id'), table_name='merchants')
    op.drop_index(op.f('ix_merchants_domain'), table_name='merchants')
    op.drop_table('merchants')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

