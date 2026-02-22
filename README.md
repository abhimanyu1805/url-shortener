# URL Shortener (Resume Project)

A production-style URL shortener API you can showcase for SDE roles.

## Highlights
- Create short links with optional custom aliases and expiration.
- Redirect short links to original URLs.
- Track click analytics (total clicks + recent click events).
- SQLite persistence using SQLModel.
- Input validation and clear error handling.
- Test suite with `pytest` + FastAPI `TestClient`.

## Tech Stack
- **Python 3.11+**
- **FastAPI**
- **SQLModel / SQLAlchemy**
- **SQLite**
- **pytest**

## Project Structure

```text
app/
  main.py          # API entrypoint and routes
  models.py        # DB models
  schemas.py       # Request/response schemas
  service.py       # Business logic
  database.py      # DB engine/session
  utils.py         # Short code generation + URL normalization
tests/
  test_api.py      # End-to-end API tests
```

## Run locally (Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Run on any device (Docker)

If Python/package setup is different on your machine, use Docker instead:

```bash
docker compose up --build
```

Then open:
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Quick local verification

```bash
curl http://127.0.0.1:8000/health
```
Expected output:
```json
{"status":"ok"}
```

## Example Usage

Create short URL:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/urls \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com/very/long/path"}'
```

Open short URL in browser:
```text
http://127.0.0.1:8000/<short_code>
```

Get analytics:
```bash
curl http://127.0.0.1:8000/api/v1/urls/<short_code>/stats
```

## Resume-friendly talking points
- Designed REST API with clean layering (routes → service → persistence).
- Added expiration and custom aliases to cover real-world requirements.
- Implemented event-level analytics for observability.
- Wrote tests for success + failure flows.

## Next improvements
- Add Redis caching for heavy redirect traffic.
- Add background jobs and async analytics aggregation.
- Add auth and per-user link ownership.
- Dockerize and deploy to cloud (Render/Fly/AWS).
