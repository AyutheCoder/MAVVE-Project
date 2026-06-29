"""
Address model — stores raw and normalized delivery addresses.
Tracks geocoding results, landmark references, and verification status.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Address(Base):
    """
    Delivery address entity.

    Captures the raw, unstructured address from rural consumers alongside
    the normalized, machine-readable version produced by the Address
    Resolution Agent.  Confidence and verification flags drive
    routing decisions in the Valmo logistics network.
    """

    __tablename__ = "addresses"

    # ── Primary Key ──────────────────────────────────────
    address_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique address record identifier",
    )

    # ── Foreign Key ──────────────────────────────────────
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Consumer who owns this address",
    )

    # ── Raw Input ────────────────────────────────────────
    raw_address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Original unstructured address string from the consumer",
    )

    # ── Normalized Output ────────────────────────────────
    normalized_address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        comment="Cleaned, structured address after agent resolution",
    )

    # ── Geography ────────────────────────────────────────
    pincode: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="6-digit Indian postal code",
    )
    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="District / tehsil name",
    )
    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="State / Union Territory",
    )

    # ── Landmarks ────────────────────────────────────────
    landmarks: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="Array of {name, type, distance_m} identified near the address",
    )

    # ── Scoring & Geocoding ──────────────────────────────
    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Address completeness / deliverability confidence (0.0 – 1.0)",
    )
    geo_lat: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None,
        comment="Latitude from geocoding",
    )
    geo_lng: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None,
        comment="Longitude from geocoding",
    )

    # ── Verification ─────────────────────────────────────
    verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if the Address Agent has confirmed this address",
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
    user = relationship("User", back_populates="addresses")

    # ── Indexes ──────────────────────────────────────────
    __table_args__ = (
        Index("ix_addresses_confidence", "confidence_score"),
        Index("ix_addresses_verified", "verified"),
    )

    def __repr__(self) -> str:
        return (
            f"<Address {self.address_id[:8]}… "
            f"pin={self.pincode} conf={self.confidence_score:.2f} "
            f"verified={self.verified}>"
        )
