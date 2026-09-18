"""ORM model for multi-platform OAuth / session credentials (ISRC sync)."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ConnectedPlatform(Base):
    """Per-user connection to Spotify, Apple Music, or Last.fm for ISRC sync.

    Kept separate from ConnectedAccount (playlist sync / demo auth) so the
    multi-platform ISRC pipeline can store platform-specific session metadata
    without changing the existing account table.
    """

    __tablename__ = "connected_platforms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    platform_name: Mapped[str] = mapped_column(String(32), nullable=False)
    platform_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_meta: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
