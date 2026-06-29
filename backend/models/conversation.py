"""
Conversation model — logs every MAVVE agent ↔ consumer interaction.
Stores full transcript, outcome, and metrics for analytics and model fine-tuning.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Conversation(Base):
    """
    MAVVE agent conversation session.

    Each conversation corresponds to a single agent handling one order.
    An order may have multiple conversations (e.g., address agent then prepaid agent).
    """

    __tablename__ = "conversations"

    # ── Primary Key ──────────────────────────────────────
    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique conversation session identifier",
    )

    # ── Foreign Key ──────────────────────────────────────
    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Order this conversation relates to",
    )

    # ── Agent Metadata ───────────────────────────────────
    agent_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="address_resolution | intent_verification | prepaid_conversion",
    )
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="whatsapp_text",
        comment="whatsapp_text | whatsapp_voice | simulator",
    )
    user_language: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        default="hi",
        comment="ISO 639-1 code of the language used in conversation",
    )

    # ── Transcript ───────────────────────────────────────
    messages: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="Array of {role, content, timestamp, language, translated}",
    )

    # ── Outcome ──────────────────────────────────────────
    outcome: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        comment="converted | confirmed | cancelled | escalated | timed_out",
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total conversation duration in seconds",
    )
    discount_applied: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Discount amount (₹) offered during prepaid negotiation",
    )

    # ── Timestamps ───────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ────────────────────────────────────
    order = relationship("Order", back_populates="conversations")

    # ── Constraints & Indexes ────────────────────────────
    __table_args__ = (
        CheckConstraint(
            "agent_type IN ('address_resolution', 'intent_verification', 'prepaid_conversion', 'orchestrator')",
            name="ck_conversation_agent_type",
        ),
        CheckConstraint(
            "outcome IS NULL OR outcome IN ('converted', 'confirmed', 'cancelled', 'escalated', 'timed_out')",
            name="ck_conversation_outcome",
        ),
        Index("ix_conversations_agent", "agent_type"),
        Index("ix_conversations_outcome", "outcome"),
        Index("ix_conversations_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Conversation {self.session_id[:8]}… "
            f"agent={self.agent_type} outcome={self.outcome} "
            f"lang={self.user_language} dur={self.duration_seconds}s>"
        )
