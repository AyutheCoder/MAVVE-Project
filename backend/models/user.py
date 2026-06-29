"""
User model — represents consumers on the platform.
Tracks purchase history, language preferences, and trust scoring.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Float,
    Integer,
    DateTime,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class User(Base):
    """
    Consumer / buyer entity.

    Stores demographic data, preferred language, and computed trust metrics
    used by the RTO risk predictor and agent orchestration.
    """

    __tablename__ = "users"

    # ── Primary Key ──────────────────────────────────────
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique consumer identifier",
    )

    # ── Identity ─────────────────────────────────────────
    phone_number: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False,
        index=True,
        comment="E.164 format phone number (e.g. +919876543210)",
    )
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        comment="Consumer display name",
    )

    # ── Language & Geography ─────────────────────────────
    preferred_language: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        default="hi",
        comment="ISO 639-1 language code (hi, mr, bn, ta, te, kn, gu)",
    )
    pincode: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        index=True,
        comment="Primary delivery pincode",
    )

    # ── Trust & Risk Metrics ─────────────────────────────
    historical_rto_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Lifetime RTO rate (0.0 – 1.0)",
    )
    total_orders: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total orders placed on platform",
    )
    total_returns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total RTO / return events",
    )
    trust_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        comment="Composite trust score (0.0 – 1.0); higher = more trustworthy",
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
    orders = relationship("Order", back_populates="user", lazy="selectin")
    addresses = relationship("Address", back_populates="user", lazy="selectin")

    # ── Indexes ──────────────────────────────────────────
    __table_args__ = (
        Index("ix_users_language", "preferred_language"),
        Index("ix_users_trust", "trust_score"),
    )

    def __repr__(self) -> str:
        return (
            f"<User {self.user_id[:8]}… "
            f"name={self.name!r} lang={self.preferred_language} "
            f"rto={self.historical_rto_rate:.2f}>"
        )
