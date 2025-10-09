# Tasks Module

Background job processing with Redis and Streaq (when enabled).

## Quick Reference

Tasks are only available if job queue was enabled during scaffolding.

## Defining Tasks

```python
from ..models import User
from .worker import worker

@worker.task()
async def send_welcome_email(user_id: str) -> dict[str, str]:
    """Example background job."""

    # Access context
    res = await worker.context.http_client.get(url)

    if user := await User.get(user_id):
        # Perform side effects
        return {"status": "sent", "user": user.email}
    return {"status": "skipped"}
```

## Queueing Tasks

```python
from ..tasks import send_welcome_email

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

Add new task modules at the end of `worker.py`:

```python
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
