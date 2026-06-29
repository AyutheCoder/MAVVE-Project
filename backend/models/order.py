"""
Order model — represents a single e-commerce transaction.
Tracks payment mode, RTO risk score, MAVVE session linkage, and status lifecycle.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Float,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Order(Base):
    """
    E-commerce order entity.

    Lifecycle:  PLACED → INTERCEPTED → VALIDATED → DISPATCHED → DELIVERED
                                                  ↘ RTO
                                     ↘ CANCELLED
    """

    __tablename__ = "orders"

    # ── Primary Key ──────────────────────────────────────
    order_id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}",
        comment="Unique order identifier (e.g. ORD-A1B2C3D4)",
    )

    # ── Foreign Keys ─────────────────────────────────────
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Consumer who placed this order",
    )
    seller_id: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="MSME seller identifier",
    )

    # ── Items & Value ────────────────────────────────────
    items: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="Array of {sku, name, qty, price, category}",
    )
    total_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Total order value in INR",
    )

    # ── Payment ──────────────────────────────────────────
    payment_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="COD",
        comment="COD | PREPAID | PREPAID_PENDING",
    )

    # ── Delivery ─────────────────────────────────────────
    delivery_address: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Structured address: {raw, line1, line2, landmark, city, district, state}",
    )
    pincode: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="Delivery pincode",
    )

    # ── Status & Risk ────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PLACED",
        index=True,
        comment="PLACED | INTERCEPTED | VALIDATED | DISPATCHED | DELIVERED | RTO | CANCELLED",
    )
    rto_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        default=None,
        comment="Predicted P(RTO) from 0.0 to 1.0",
    )

    # ── MAVVE Session ────────────────────────────────────
    mavve_session_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        default=None,
        index=True,
        comment="Links to the MAVVE conversation session (if intercepted)",
    )

    # ── Timestamps ───────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────
    user = relationship("User", back_populates="orders")
    conversations = relationship(
        "Conversation", back_populates="order", lazy="selectin"
    )

    # ── Constraints & Indexes ────────────────────────────
    __table_args__ = (
        CheckConstraint(
            "payment_mode IN ('COD', 'PREPAID', 'PREPAID_PENDING')",
            name="ck_order_payment_mode",
        ),
        CheckConstraint(
            "status IN ('PLACED','INTERCEPTED','VALIDATED','DISPATCHED','DELIVERED','RTO','CANCELLED')",
            name="ck_order_status",
        ),
        CheckConstraint(
            "total_amount > 0",
            name="ck_order_amount_positive",
        ),
        Index("ix_orders_risk", "rto_risk_score"),
        Index("ix_orders_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Order {self.order_id} "
            f"₹{self.total_amount:.0f} {self.payment_mode} "
            f"status={self.status} risk={self.rto_risk_score}>"
        )
