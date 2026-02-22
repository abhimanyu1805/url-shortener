from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from app.models import ClickEvent, URLMapping
from app.schemas import ShortenURLRequest
from app.utils import generate_short_code


MAX_GENERATION_ATTEMPTS = 10


def _is_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return False
    return expires_at <= datetime.now(timezone.utc)


def create_short_url(session: Session, payload: ShortenURLRequest) -> URLMapping:
    if payload.expires_at and payload.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expires_at must be in the future",
        )

    short_code = payload.custom_alias
    if short_code:
        existing = session.exec(select(URLMapping).where(URLMapping.short_code == short_code)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="custom alias is already taken",
            )
    else:
        for _ in range(MAX_GENERATION_ATTEMPTS):
            candidate = generate_short_code()
            existing = session.exec(select(URLMapping).where(URLMapping.short_code == candidate)).first()
            if not existing:
                short_code = candidate
                break
        if short_code is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="failed to generate unique short code",
            )

    entry = URLMapping(
        short_code=short_code,
        original_url=str(payload.original_url),
        expires_at=payload.expires_at,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def get_url_mapping(session: Session, short_code: str) -> URLMapping:
    entry = session.exec(select(URLMapping).where(URLMapping.short_code == short_code)).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="short code not found")
    if _is_expired(entry.expires_at):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="short code expired")
    return entry


def record_click(
    session: Session,
    short_code: str,
    user_agent: str | None,
    referrer: str | None,
) -> ClickEvent:
    click = ClickEvent(short_code=short_code, user_agent=user_agent, referrer=referrer)
    session.add(click)
    session.commit()
    session.refresh(click)
    return click


def get_url_stats(session: Session, short_code: str) -> tuple[URLMapping, int, list[ClickEvent]]:
    entry = session.exec(select(URLMapping).where(URLMapping.short_code == short_code)).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="short code not found")

    total_clicks = session.exec(
        select(func.count(ClickEvent.id)).where(ClickEvent.short_code == short_code)
    ).one()

    recent_clicks = session.exec(
        select(ClickEvent)
        .where(ClickEvent.short_code == short_code)
        .order_by(ClickEvent.clicked_at.desc())
        .limit(20)
    ).all()

    return entry, int(total_clicks or 0), recent_clicks
