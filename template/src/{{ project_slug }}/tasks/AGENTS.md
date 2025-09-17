# Tasks Module

Background job processing with Redis and Streaq (when enabled).

## Setup

The queue is provisioned only when the job-runner option is selected during
scaffolding.

## Defining Tasks

Tasks are attached to the shared worker declared in `worker.py`.

```python
from ..models import User
from .worker import worker


@worker.task()
async def send_welcome_email(user_id: str) -> dict[str, str]:
    """Example background job."""
    
    # Access the context this way
    res = await worker.context.http_client.get(url)

    if user := await User.get(user_id):
        # perform side effects here (email, webhook, etc.)
        return {"status": "sent", "user": user.email}
    return {"status": "skipped"}
```

Key points:

- Decorate functions with `@worker.task()` so they register automatically.
- You can access the context via worker.context from within the tasks
- Context resources are defined in `tasks/context.py`
- Return serializable data; it is stored in Redis for retrieval.

## Queueing Tasks From Routes or Services

Import the registered task and call its `enqueue` helper directly.

```python
from ..tasks import send_welcome_email


@router.post("/signup")
async def signup(email: str):
    user = await create_user(email)

    task = await send_welcome_email.enqueue(user.id)
    # Optional: inspect task.id or await task.result()

    return {"status": "registered", "job_id": task.id}
```

`RegisteredTask.enqueue()` returns a `Task` handle (`task.id`,
`await task.status()`, `await task.result(timeout=...)`) that you can use for
polling or surfacing status updates.

## Worker Management

```bash
# Development
just worker-dev                 # Run worker locally with auto-reload
```

The `start.sh` script already wires the recommended commands for local and
containerised environments.

## Worker Configuration

`tasks/worker.py` initialises the shared worker used across the app.

```python
from streaq import Worker
from ..core.config import project_settings, settings
from .context import lifespan


worker = Worker(
    redis_url=str(project_settings.redis_url),
    queue_name=(
        project_settings.project_slug
        if not settings.debug
        else f"debug-{project_settings.project_slug}"
    ),
    lifespan=lifespan,
)

# Import modules at the bottom of this file so their tasks register.
from . import emails  # noqa: E402, F401
```

When adding a new task module, import it at the end of `worker.py` (or
`tasks/__init__.py`) so the decorator runs and the task is visible to the
worker.

## Monitoring & Diagnostics

```python
task = await send_digest_email.enqueue(account_id)

status = await task.status()
result = await task.result(timeout=30)  # raises TimeoutError if it takes too long
await task.abort()                      # request cancellation when required
```
