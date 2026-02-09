# Core Tasks Module

**IMMUTABLE SCAFFOLDING CODE** - This is the framework's core background task infrastructure.

> **Package name convention**: Where this document references `src/app/` or `from app.`,
> `app` is a placeholder for the user's actual Python package name (the directory under `src/`,
> derived from their project slug).

## What's Here

This module contains the scaffolding's core task components:

- **worker.py** - Streaq worker setup and configuration
- **context.py** - Task context management (DB, HTTP client, etc.)
- ****init**.py** - Task infrastructure exports

## Important Rules

⚠️ **DO NOT MODIFY** these core task components directly.

**For changes to core tasks:**

- File an issue at `https://github.com/alltuner/vibetuner`
- Core changes benefit all projects using the scaffolding

**For your application tasks:**

- Create them in `src/app/tasks/` instead
- Import the worker using `get_worker()` for type-safe access

## Quick Reference

Tasks are only available if job queue was enabled during scaffolding.

The worker is defined in `vibetuner.tasks.worker`. Use `get_worker()` to import it with proper type
checking (returns `Worker` instead of `Worker | None`).

## User Task Pattern (for reference)

Your application tasks in `src/app/tasks/` should follow this pattern:

```python
# src/app/tasks/emails.py
from vibetuner.models import UserModel
from vibetuner.tasks.worker import get_worker

worker = get_worker()

@worker.task()
async def send_welcome_email(user_id: str) -> dict[str, str]:
    """Example background job."""

    # Access context
    res = await worker.context.http_client.get(url)

    if user := await UserModel.get(user_id):
        # Perform side effects
        return {"status": "sent", "user": user.email}
    return {"status": "skipped"}
```

## Queueing Tasks

```python
# In your routes: src/app/frontend/routes/auth.py
from app.tasks.emails import send_welcome_email

@router.post("/signup")
async def signup(email: str):
    user = await create_user(email)

    task = await send_welcome_email.enqueue(user.id)
    # Optional: await task.result() or check task.id

    return {"status": "registered", "job_id": task.id}
```

Note: Import your task functions from `src/app/tasks/` but the worker itself comes from `vibetuner.tasks.worker`.

## Worker Management

```bash
just worker-dev    # Run worker locally with auto-reload
```

## Task Registration

Add new task modules at the end of `src/app/tasks/__init__.py`:

```python
# src/app/tasks/__init__.py
# Import your task modules so decorators register with worker
from . import emails  # noqa: F401
from . import new_tasks  # noqa: F401
```

## Monitoring

```python
task = await send_digest_email.enqueue(account_id)

status = await task.status()
result = await task.result(timeout=30)
await task.abort()  # Cancel if needed
```
