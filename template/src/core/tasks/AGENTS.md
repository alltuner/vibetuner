# Core Tasks Module

**IMMUTABLE SCAFFOLDING CODE** - This is the framework's core background task infrastructure.

## What's Here

This module contains the scaffolding's core task components:

- **worker.py** - Streaq worker setup and configuration
- **context.py** - Task context management (DB, HTTP client, etc.)
- ****init**.py** - Task infrastructure exports

## Important Rules

⚠️  **DO NOT MODIFY** these core task components directly.

**For changes to core tasks:**

- File an issue at `https://github.com/alltuner/scaffolding`
- Core changes benefit all projects using the scaffolding

**For your application tasks:**

- Create them in `src/app/tasks/` instead
- Import the worker from app: `from app.tasks.worker import worker`

## Quick Reference

Tasks are only available if job queue was enabled during scaffolding.

## User Task Pattern (for reference)

Your application tasks in `src/app/tasks/` should follow this pattern:

```python
# src/app/tasks/emails.py
from core.models import UserModel
from app.tasks.worker import worker

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

## Worker Management

```bash
just worker-dev    # Run worker locally with auto-reload
```

## Task Registration

Add new task modules at the end of `src/app/tasks/worker.py`:

```python
# src/app/tasks/worker.py
from core.tasks.worker import worker  # Import core worker

# Import at bottom so decorator runs
from . import emails  # noqa: E402, F401
from . import new_tasks  # noqa: E402, F401
```

## Monitoring

```python
task = await send_digest_email.enqueue(account_id)

status = await task.status()
result = await task.result(timeout=30)
await task.abort()  # Cancel if needed
```
