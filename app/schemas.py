from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class ShortenURLRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        if not (3 <= len(value) <= 12):
            raise ValueError("custom_alias length must be between 3 and 12")
        if any(char not in allowed for char in value):
            raise ValueError("custom_alias contains invalid characters")
        return value


class ShortenURLResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    expires_at: Optional[datetime] = None


class ClickEventResponse(BaseModel):
    clicked_at: datetime
    user_agent: Optional[str]
    referrer: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class URLStatsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    total_clicks: int
    recent_clicks: list[ClickEventResponse]

    model_config = ConfigDict(from_attributes=True)
