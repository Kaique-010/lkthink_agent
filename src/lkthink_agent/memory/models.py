
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class MemoryBase(DeclarativeBase):
    pass

class MemoryORM(MemoryBase):
    __tablename__ = "lkthink_memories"

    __table_args__ = (
        Index(
            "ix_lkthink_memory_scope",
            "agent_id",
            "user_id",
            "session_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    agent_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    session_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="general",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

@dataclass(frozen=True, slots=True)
class MemoryItem:
    id: str
    agent_id: str
    user_id: str
    session_id: str | None
    category: str
    content: str
    metadata: dict = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None