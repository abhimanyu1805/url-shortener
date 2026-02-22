from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.database import create_db_and_tables, get_session
from app.schemas import ShortenURLRequest, ShortenURLResponse, URLStatsResponse
from app.service import create_short_url, get_url_mapping, get_url_stats, record_click


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="URL Shortener", version="1.0.0", lifespan=lifespan)


def session_dep() -> Session:
    with get_session() as session:
        yield session


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/urls", response_model=ShortenURLResponse, status_code=201)
def shorten_url(
    payload: ShortenURLRequest,
    request: Request,
    session: Session = Depends(session_dep),
) -> ShortenURLResponse:
    entry = create_short_url(session, payload)
    base_url = str(request.base_url).rstrip("/")
    return ShortenURLResponse(
        short_code=entry.short_code,
        short_url=f"{base_url}/{entry.short_code}",
        original_url=entry.original_url,
        expires_at=entry.expires_at,
    )


@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    request: Request,
    session: Session = Depends(session_dep),
) -> RedirectResponse:
    entry = get_url_mapping(session, short_code)
    record_click(
        session=session,
        short_code=short_code,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
    )
    return RedirectResponse(url=entry.original_url, status_code=307)


@app.get("/api/v1/urls/{short_code}/stats", response_model=URLStatsResponse)
def url_stats(short_code: str, session: Session = Depends(session_dep)) -> URLStatsResponse:
    entry, total_clicks, recent_clicks = get_url_stats(session, short_code)
    return URLStatsResponse(
        short_code=entry.short_code,
        original_url=entry.original_url,
        created_at=entry.created_at,
        expires_at=entry.expires_at,
        total_clicks=total_clicks,
        recent_clicks=recent_clicks,
    )
