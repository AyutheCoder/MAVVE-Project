"""create initial tables

Revision ID: 001_initial
Revises: None
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Users Table ──────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("phone_number", sa.String(15), unique=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("preferred_language", sa.String(5), nullable=False, server_default="hi"),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("historical_rto_rate", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("total_orders", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_returns", sa.Integer, nullable=False, server_default="0"),
        sa.Column("trust_score", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_phone_number", "users", ["phone_number"])
    op.create_index("ix_users_pincode", "users", ["pincode"])
    op.create_index("ix_users_language", "users", ["preferred_language"])
    op.create_index("ix_users_trust", "users", ["trust_score"])

    # ── Orders Table ─────────────────────────────────────
    op.create_table(
        "orders",
        sa.Column("order_id", sa.String(32), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("seller_id", sa.String(32), nullable=False),
        sa.Column("items", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("total_amount", sa.Float, nullable=False),
        sa.Column("payment_mode", sa.String(20), nullable=False, server_default="COD"),
        sa.Column("delivery_address", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("pincode", sa.String(10), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PLACED"),
        sa.Column("rto_risk_score", sa.Float, nullable=True),
        sa.Column("mavve_session_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("payment_mode IN ('COD', 'PREPAID', 'PREPAID_PENDING')", name="ck_order_payment_mode"),
        sa.CheckConstraint("status IN ('PLACED','INTERCEPTED','VALIDATED','DISPATCHED','DELIVERED','RTO','CANCELLED')", name="ck_order_status"),
        sa.CheckConstraint("total_amount > 0", name="ck_order_amount_positive"),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_seller_id", "orders", ["seller_id"])
    op.create_index("ix_orders_pincode", "orders", ["pincode"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_risk", "orders", ["rto_risk_score"])
    op.create_index("ix_orders_mavve_session", "orders", ["mavve_session_id"])
    op.create_index("ix_orders_created", "orders", ["created_at"])

    # ── Conversations Table ──────────────────────────────
    op.create_table(
        "conversations",
        sa.Column("session_id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("order_id", sa.String(32), sa.ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_type", sa.String(30), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False, server_default="whatsapp_text"),
        sa.Column("user_language", sa.String(5), nullable=False, server_default="hi"),
        sa.Column("messages", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("outcome", sa.String(20), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=False, server_default="0"),
        sa.Column("discount_applied", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "agent_type IN ('address_resolution', 'intent_verification', 'prepaid_conversion', 'orchestrator')",
            name="ck_conversation_agent_type",
        ),
        sa.CheckConstraint(
            "outcome IS NULL OR outcome IN ('converted', 'confirmed', 'cancelled', 'escalated', 'timed_out')",
            name="ck_conversation_outcome",
        ),
    )
    op.create_index("ix_conversations_order_id", "conversations", ["order_id"])
    op.create_index("ix_conversations_agent", "conversations", ["agent_type"])
    op.create_index("ix_conversations_outcome", "conversations", ["outcome"])
    op.create_index("ix_conversations_created", "conversations", ["created_at"])

    # ── Addresses Table ──────────────────────────────────
    op.create_table(
        "addresses",
        sa.Column("address_id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_address", sa.String(500), nullable=False),
        sa.Column("normalized_address", sa.String(500), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=False),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("landmarks", postgresql.JSONB, nullable=True),
        sa.Column("confidence_score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("geo_lat", sa.Float, nullable=True),
        sa.Column("geo_lng", sa.Float, nullable=True),
        sa.Column("verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_addresses_user_id", "addresses", ["user_id"])
    op.create_index("ix_addresses_pincode", "addresses", ["pincode"])
    op.create_index("ix_addresses_confidence", "addresses", ["confidence_score"])
    op.create_index("ix_addresses_verified", "addresses", ["verified"])


def downgrade() -> None:
    op.drop_table("addresses")
    op.drop_table("conversations")
    op.drop_table("orders")
    op.drop_table("users")
