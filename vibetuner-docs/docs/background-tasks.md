# Background Tasks

Run long-running or scheduled work outside the request cycle using Vibetuner's
background task system, powered by
[Streaq](https://github.com/samuelcolvin/streaq) and Redis.

<!-- markdownlint-disable MD046 -->

!!! note "Package name convention"
    In all examples, `app` refers to your project's Python package (the directory
    under `src/`). The actual name depends on your project slug (e.g.,
    `src/myproject/` for a project named "myproject").

## Prerequisites

Background tasks require **Redis**. Set the `REDIS_URL` environment variable in
your `.env` file:

```bash
REDIS_URL=redis://localhost:6379
```

When using Docker development (`just dev`), Redis is started automatically.
For local development, install and start Redis separately or use the Docker
Compose services.

## Quick Start

### 1. Create a Task

Create a task file in `src/app/tasks/`:

```python
# src/app/tasks/emails.py
from vibetuner.tasks.worker import get_worker

worker = get_worker()

@worker.task()
async def send_welcome_email(user_id: str) -> dict[str, str]:
    """Send a welcome email to a newly registered user."""
    from vibetuner.models import UserModel
    from vibetuner.services.email import send_email

    user = await UserModel.get(user_id)
    if user:
        await send_email(
            to_email=user.email,
            subject="Welcome!",
            html_content="<h1>Welcome!</h1>",
        )
        return {"status": "sent", "email": user.email}
    return {"status": "skipped"}
```

### 2. Register the Task

List the task function in your `tune.py`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.tasks.emails import send_welcome_email

app = VibetunerApp(
    tasks=[send_welcome_email],
)
```

### 3. Enqueue from a Route

```python
# src/app/frontend/routes/auth.py
from app.tasks.emails import send_welcome_email

@router.post("/signup")
async def signup(email: str):
    user = await create_user(email)
    task = await send_welcome_email.enqueue(str(user.id))
    return {"message": "Welcome email queued", "task_id": task.id}
```

### 4. Start the Worker

```bash
# Recommended: using justfile
just worker-dev

# Or manually:
uv run vibetuner run dev worker

# With Docker, Redis + app start automatically:
just dev
```

The worker picks up queued tasks and executes them in the background.

## Creating Tasks

### Basic Task

Every task is an async function decorated with `@worker.task()`:

```python
# src/app/tasks/reports.py
from vibetuner.tasks.worker import get_worker

worker = get_worker()

@worker.task()
async def generate_report(account_id: str) -> dict:
    """Generate a monthly report for an account."""
    # ... long-running work ...
    return {"status": "complete", "account_id": account_id}
```

### Task with Timeout

Set a maximum execution time for a task:

```python
from datetime import timedelta

@worker.task(timeout=timedelta(minutes=5))
async def process_large_file(file_id: str) -> dict:
    # Aborted if it takes longer than 5 minutes
    ...
```

### Task Organization

Group related tasks in separate modules under `src/app/tasks/`:

```text
src/app/tasks/
├── __init__.py
├── emails.py          # Email-related tasks
├── reports.py         # Report generation
└── notifications.py   # Push notifications
```

Register all task functions in `tune.py`:

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.tasks.emails import send_welcome_email, send_digest
from app.tasks.reports import generate_report
from app.tasks.notifications import send_push

app = VibetunerApp(
    tasks=[send_welcome_email, send_digest, generate_report, send_push],
)
```

## Worker Dependency Injection

Use `WorkerDepends()` from Streaq to inject the worker context into your tasks.
The context provides access to shared resources initialized during the worker
lifespan (such as HTTP clients and database connections):

```python
from streaq import WorkerDepends
from vibetuner.tasks.worker import get_worker

worker = get_worker()

@worker.task()
async def fetch_external_data(url: str, ctx=WorkerDepends()) -> dict:
    """Fetch data using the shared HTTP client from worker context."""
    response = await ctx.http_client.get(url)
    return {"status": response.status_code, "data": response.text[:100]}
```

The `ctx` parameter receives the context object yielded by the worker lifespan.
By default, this is a `Context` instance with project metadata. You can extend
it with a custom worker lifespan (see [Worker Lifecycle](#worker-lifecycle)).

## The `@robust_task()` Decorator

For tasks that need automatic retries and dead letter tracking, use the
`@robust_task()` decorator instead of `@worker.task()`:

```python
from vibetuner.tasks.robust import robust_task

@robust_task(max_retries=5, backoff_max=600)
async def send_webhook(payload: dict) -> dict:
    """Send a webhook with automatic retries on failure."""
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.post("https://example.com/hook", json=payload)
        resp.raise_for_status()
    return {"status": "delivered"}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_retries` | `int` | `3` | Maximum attempts before giving up |
| `backoff_base` | `float` | `2.0` | Base for exponential backoff (`delay = base ** tries`) |
| `backoff_max` | `float` | `300.0` | Maximum backoff delay in seconds |
| `timeout` | `timedelta \| int \| None` | `None` | Task timeout (forwarded to `worker.task()`) |
| `on_failure` | `Callable \| None` | `None` | Called on permanent failure (sync or async) |
| `**task_kwargs` | | | Extra keyword arguments forwarded to `worker.task()` |

### Retry Behavior

When a task raises an exception:

1. If `tries < max_retries`, the task is retried after an exponential backoff
   delay: `min(backoff_base ** tries, backoff_max)` seconds.
2. If all retries are exhausted, the task is recorded in the `dead_letters`
   MongoDB collection and the optional `on_failure` callback is invoked.

### Dead Letter Collection

Permanently failed tasks are stored in the `dead_letters` MongoDB collection
with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `task_name` | `str` | Function name of the failed task |
| `task_id` | `str` | Unique task identifier |
| `error` | `str` | Error message |
| `error_type` | `str` | Exception class name |
| `tries` | `int` | Number of attempts made |
| `failed_at` | `datetime` | Timestamp of permanent failure |

### Failure Callback

The `on_failure` callback receives three arguments and can be sync or async:

```python
async def alert_on_failure(task_name: str, task_id: str, exc: Exception):
    """Send an alert when a task permanently fails."""
    await notify_ops_team(f"Task {task_name} ({task_id}) failed: {exc}")

@robust_task(max_retries=3, on_failure=alert_on_failure)
async def critical_sync(data: dict):
    ...
```

## Scheduled Tasks (Cron)

Use `@worker.cron()` to run tasks on a schedule:

```python
from vibetuner.tasks.worker import get_worker

worker = get_worker()

@worker.cron("0 9 * * *")  # Every day at 9:00 AM UTC
async def daily_digest():
    """Send daily digest emails to all subscribed users."""
    ...

@worker.cron("*/15 * * * *")  # Every 15 minutes
async def check_expired_sessions():
    """Clean up expired sessions."""
    ...
```

The cron expression follows standard crontab syntax:

```text
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

Register cron tasks in `tune.py` the same way as regular tasks:

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.tasks.maintenance import daily_digest, check_expired_sessions

app = VibetunerApp(
    tasks=[daily_digest, check_expired_sessions],
)
```

!!! note
    Cron tasks are only executed by the worker process. They will not run
    if the worker is not started.

## Enqueueing and Monitoring Tasks

### Enqueue a Task

```python
from app.tasks.emails import send_welcome_email

# Enqueue with arguments
task = await send_welcome_email.enqueue(user_id)
```

### Check Task Status

```python
# Get current status
status = await task.status()

# Wait for result with timeout
task_result = await task.result(timeout=30)

if task_result.success:
    value = task_result.result
else:
    error = task_result.exception
```

### Cancel a Task

```python
await task.abort()
```

## SSE Integration

Broadcast real-time updates from background tasks to connected clients using
Server-Sent Events. This is useful for progress indicators, live feeds, and
notifications.

```python
from vibetuner.sse import broadcast
from vibetuner.tasks.worker import get_worker

worker = get_worker()

@worker.task()
async def process_upload(file_id: str, user_id: str) -> dict:
    """Process an uploaded file and broadcast progress."""
    channel = f"upload:{user_id}"

    await broadcast(channel, "progress", data="Processing started...")

    # ... do work ...

    await broadcast(channel, "progress", data="50% complete...")

    # ... more work ...

    await broadcast(
        channel,
        "complete",
        data="<div class='alert alert-success'>Upload complete!</div>",
    )
    return {"status": "complete"}
```

!!! warning
    Broadcasting from a task requires Redis. The `broadcast()` function
    uses Redis pub/sub to relay events across processes (the worker
    process to the frontend process). Without Redis, broadcasts from
    tasks will not reach connected clients.

On the frontend, subscribe with HTMX:

```html
<div hx-ext="sse"
     sse-connect="/events/upload/{{ user.id }}"
     sse-swap="progress complete">
</div>
```

With a corresponding SSE endpoint:

```python
from vibetuner.sse import sse_endpoint

@sse_endpoint("/events/upload/{user_id}", router=router)
async def upload_stream(request: Request, user_id: str):
    return f"upload:{user_id}"
```

For more details on SSE, see the
[SSE / Real-Time Streaming](development-guide.md#sse-real-time-streaming)
section in the development guide.

## Worker Lifecycle

### Default Behavior

The worker automatically initializes MongoDB and SQLModel connections on startup
and tears them down on shutdown. The default lifespan yields a `Context` object
with project metadata.

### Custom Worker Lifespan

To add custom startup/shutdown logic or extend the worker context, create a
custom lifespan and pass it to `tune.py`:

```python
# src/app/tasks/lifespan.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from vibetuner.context import Context, ctx
from vibetuner.tasks.lifespan import base_lifespan


@asynccontextmanager
async def worker_lifespan() -> AsyncGenerator[Context, None]:
    """Custom worker lifespan with additional setup."""
    async with base_lifespan() as context:
        # Custom startup logic
        print("Worker starting with custom setup")
        yield context
        # Custom shutdown logic
        print("Worker shutting down")
```

```python
# src/app/tune.py
from vibetuner import VibetunerApp
from app.tasks.lifespan import worker_lifespan

app = VibetunerApp(
    worker_lifespan=worker_lifespan,
)
```

!!! note
    The base lifespan handles MongoDB and SQLModel initialization. Always
    wrap it with `async with base_lifespan() as context:` when providing
    a custom lifespan to retain database connectivity.

## Streaq Task Dashboard

When workers are configured, a built-in monitoring UI is available at
**`/debug/tasks`**. This dashboard shows:

- Active, queued, and completed tasks
- Task execution times and results
- Failed tasks and error details
- Worker health and concurrency

The dashboard is protected by the same debug access controls as other
`/debug/*` endpoints. In development mode (`DEBUG=true`), it is accessible
without authentication. In production, use the
`/_unlock-debug?token=<DEBUG_ACCESS_TOKEN>` endpoint to gain access.

A standalone worker monitoring web UI also starts automatically on
**port 11111** when you run the worker. Access it at
`http://localhost:11111`.

## Running Workers

### Development

```bash
# Worker only
just worker-dev

# Everything: server + assets + worker
just local-all-with-worker

# Worker only (with hot reload, manual)
uv run vibetuner run dev worker

# Custom port for the monitoring UI
uv run vibetuner run dev worker --port 12000
```

In development mode, the worker runs with hot reload enabled. Code changes
automatically restart the worker process.

### Production

The production compose file (`compose.prod.yml`) runs the worker as a
separate service:

```yaml
services:
  worker:
    image: your-registry/your-app:latest
    command: ["prod", "worker"]
    env_file:
      - .env
```

```bash
docker compose -f compose.prod.yml up
```

Or run manually without Docker:

```bash
vibetuner run prod worker --workers 4
```

### Configuration

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Redis URL | `REDIS_URL` | None | Redis connection string (required) |
| Concurrency | `WORKER_CONCURRENCY` | `16` | Max concurrent tasks per worker |
| Queue name | — | Project slug | Derived from `REDIS_KEY_PREFIX` |
| Monitoring port | `--port` flag | `11111` | Port for the worker web UI |

## Testing Tasks

Use the `mock_tasks` fixture to test task enqueuing without Redis:

```python
from unittest.mock import patch

async def test_signup_queues_email(vibetuner_client, mock_tasks):
    with patch(
        "app.tasks.emails.send_welcome_email",
        mock_tasks.send_welcome_email,
    ):
        resp = await vibetuner_client.post(
            "/signup", data={"email": "a@b.com"}
        )
    assert mock_tasks.send_welcome_email.enqueue.called
```

For testing task logic directly (without enqueuing), call the function:

```python
async def test_send_welcome_email(vibetuner_db):
    from app.tasks.emails import send_welcome_email

    # Create a test user first
    user = await create_test_user()
    result = await send_welcome_email(str(user.id))
    assert result["status"] == "sent"
```

## Troubleshooting

### "Redis not configured" Error

The worker requires `REDIS_URL` to be set. Add it to your `.env`:

```bash
REDIS_URL=redis://localhost:6379
```

If using Docker, Redis starts automatically with `just dev`.

### Tasks Not Executing

1. **Is the worker running?** Check with `just worker-dev` or look for the
   worker process in Docker logs.
2. **Is the task registered?** Make sure the task function is listed in
   `VibetunerApp.tasks` in `tune.py`.
3. **Is Redis reachable?** Run `vibetuner doctor` to check service
   connectivity.

### Tasks Failing Silently

Check the worker logs. In development mode, set `DEBUG=true` for verbose
output. For tasks using `@robust_task()`, check the `dead_letters` MongoDB
collection for permanently failed tasks.

### Cron Tasks Not Running

Cron tasks only execute inside the worker process. If you only have
`just local-all` running (without the worker), cron tasks will not fire.
Use `just local-all-with-worker` or start the worker separately with
`just worker-dev`.

## Next Steps

- [SSE / Real-Time Streaming](development-guide.md#sse-real-time-streaming) —
  Push live updates to the browser
- [Deployment](deployment.md) — Run workers in production
- [CLI Reference](cli-reference.md) — Full `vibetuner run` command details
- [Architecture](architecture.md) — System design overview
