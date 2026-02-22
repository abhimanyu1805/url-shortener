from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class URLMapping(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(index=True, unique=True, max_length=12)
    original_url: str
    created_at: datetime = Field(default_factory=now_utc, nullable=False)
    expires_at: Optional[datetime] = Field(default=None, nullable=True)


class ClickEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_code: str = Field(index=True, max_length=12)
    clicked_at: datetime = Field(default_factory=now_utc, nullable=False)
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
