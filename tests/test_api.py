from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

os.environ["DATABASE_URL"] = "sqlite:///./test_url_shortener.db"

from app.main import app, session_dep  # noqa: E402


test_engine = create_engine(
    "sqlite:///./test_url_shortener.db", connect_args={"check_same_thread": False}
)



def override_session_dep():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[session_dep] = override_session_dep
client = TestClient(app)



def setup_function() -> None:
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)



def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_create_and_redirect_and_stats() -> None:
    create_response = client.post(
        "/api/v1/urls",
        json={"original_url": "https://example.com/my/very/long/url"},
    )
    assert create_response.status_code == 201

    payload = create_response.json()
    assert payload["short_code"]
    assert payload["short_url"].endswith(payload["short_code"])

    redirect_response = client.get(f"/{payload['short_code']}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/my/very/long/url"

    stats_response = client.get(f"/api/v1/urls/{payload['short_code']}/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_clicks"] == 1
    assert len(stats["recent_clicks"]) == 1



def test_custom_alias_conflict() -> None:
    body = {"original_url": "https://example.com", "custom_alias": "myalias"}
    first = client.post("/api/v1/urls", json=body)
    assert first.status_code == 201

    second = client.post("/api/v1/urls", json=body)
    assert second.status_code == 409



def test_expired_link_returns_410() -> None:
    expired_at = (datetime.now(timezone.utc) + timedelta(milliseconds=100)).isoformat()
    create_response = client.post(
        "/api/v1/urls",
        json={"original_url": "https://example.com", "custom_alias": "soonexp", "expires_at": expired_at},
    )
    assert create_response.status_code == 201

    import time

    time.sleep(0.2)
    redirect_response = client.get("/soonexp", follow_redirects=False)
    assert redirect_response.status_code == 410
