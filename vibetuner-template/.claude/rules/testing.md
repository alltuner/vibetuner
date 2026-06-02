---
paths:
  - tests/**
  - conftest.py
description: Test fixtures, patterns, and mock utilities
---

# Testing

Fixtures (auto-discovered): `vibetuner_client`, `vibetuner_app`,
`vibetuner_db`, `mock_auth` (`.login()`/`.logout()`), `mock_tasks`,
`override_config`.

```python
@pytest.mark.asyncio
async def test_dashboard(vibetuner_client, mock_auth):
    mock_auth.login(name="Alice", email="alice@example.com")
    resp = await vibetuner_client.get("/dashboard")
    assert resp.status_code == 200
```

`vibetuner_db` creates a throwaway database on the configured Mongo
*server* (it never touches your project DB). It targets `MONGODB_URL`
unless `TEST_MONGODB_URL` is set. If `.env` points `MONGODB_URL` at a
remote/prod cluster, set `TEST_MONGODB_URL=mongodb://localhost:27017/`
so the suite runs locally instead of reaching prod. The session start
logs the resolved server + DB name.

Dev server must be running (`just local-all`). Playwright MCP available
at `http://localhost:8000`.
