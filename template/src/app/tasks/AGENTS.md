# Application Background Tasks

**YOUR BACKGROUND JOBS GO HERE** - Define asynchronous tasks using Streaq worker.

## What Goes Here

Create your application-specific background tasks in this directory:

- Email notifications
- Report generation
- Data processing pipelines
- Scheduled jobs
- Long-running operations
- Any work that shouldn't block HTTP responses

## Important Note

**Background tasks are only available if job queue was enabled during scaffolding.**

If job queue wasn't enabled, this directory exists but has no functionality. You
would need to re-scaffold or file an issue to add task support.

## Task Pattern

```python
# emails.py
from core.models import UserModel
from app.tasks.worker import worker
from core.services.email import send_email

@worker.task()
async def send_welcome_email(user_id: str) -> dict[str, str]:
    """Send welcome email to new user."""

    # Access context for HTTP client, etc.
    # ctx = worker.context

    user = await UserModel.get(user_id)
    if not user:
        return {"status": "skipped", "reason": "user_not_found"}

    await send_email(
        to_email=user.email,
        subject="Welcome!",
        html_content=f"<h1>Welcome {user.display_name}!</h1>",
        text_content=f"Welcome {user.display_name}!"
    )

    return {"status": "sent", "user_email": user.email}

@worker.task()
async def send_daily_digest() -> dict:
    """Send daily digest to all users."""
    users = await UserModel.find_all().to_list()

    sent_count = 0
    for user in users:
        # Process each user...
        sent_count += 1

    return {"sent_count": sent_count}
```

## Worker Setup

The `worker.py` file sets up the Streaq worker:

```python
# worker.py
from core.tasks.worker import worker

# Import your task modules at the bottom
# so the @worker.task() decorator can register them
from . import emails  # noqa: E402, F401
from . import reports  # noqa: E402, F401
from . import cleanup  # noqa: E402, F401
```

## Queueing Tasks

Queue tasks from your routes or services:

```python
# In routes:
from app.tasks.emails import send_welcome_email

@router.post("/signup")
async def signup(email: str):
    # Create user
    user = await create_user(email)

    # Queue background task
    task = await send_welcome_email.enqueue(user.id)

    # Optionally get task ID
    task_id = task.id

    return {"user_id": str(user.id), "task_id": task_id}
```

## Task Context

Access shared resources through worker context:

```python
@worker.task()
async def fetch_external_data(url: str) -> dict:
    """Fetch data from external API."""

    # HTTP client is available in context
    http_client = worker.context.http_client

    response = await http_client.get(url)
    return response.json()
```

## Task Management

### Monitoring

```python
# Get task status
from app.tasks.emails import send_welcome_email

task = await send_welcome_email.enqueue(user_id)

# Check status
status = await task.status()  # "pending", "running", "completed", "failed"

# Get result (waits if not complete)
result = await task.result(timeout=30)

# Abort running task
await task.abort()
```

### Retries

```python
@worker.task(max_retries=3, retry_delay=60)
async def unreliable_task(data: str) -> dict:
    """Task that might fail and should retry."""
    try:
        # Do something that might fail
        result = await external_api_call(data)
        return {"status": "success", "data": result}
    except Exception as e:
        # Will automatically retry up to 3 times
        raise
```

### Task Scheduling

```python
from datetime import datetime, timedelta

# Schedule for later
task = await send_welcome_email.enqueue(
    user_id,
    scheduled_at=datetime.now() + timedelta(hours=1)
)

# Recurring tasks need external scheduling (cron, etc.)
```

## Common Patterns

### Email Notifications

```python
# emails.py
from core.models import UserModel
from app.tasks.worker import worker
from core.services.email import send_email

@worker.task()
async def send_password_reset(user_id: str, token: str) -> dict:
    """Send password reset email."""
    user = await UserModel.get(user_id)
    if not user:
        return {"status": "error", "reason": "user_not_found"}

    reset_url = f"https://example.com/reset?token={token}"

    await send_email(
        to_email=user.email,
        subject="Reset Your Password",
        html_content=f"<a href='{reset_url}'>Reset Password</a>",
        text_content=f"Reset your password: {reset_url}"
    )

    return {"status": "sent"}
```

### Report Generation

```python
# reports.py
from app.models.order import Order
from app.services.export import export_service
from core.services.blob import blob_service

@worker.task()
async def generate_sales_report(start_date: str, end_date: str) -> dict:
    """Generate sales report for date range."""

    # Fetch data
    orders = await Order.find(
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).to_list()

    # Generate report
    report_bytes = await export_service.create_pdf_report(orders)

    # Upload to storage
    blob = await blob_service.upload(
        report_bytes,
        f"reports/sales_{start_date}_{end_date}.pdf"
    )

    return {
        "status": "completed",
        "blob_id": str(blob.id),
        "order_count": len(orders)
    }
```

### Data Processing

```python
# processing.py
from app.models.image import ImageModel
from app.services.image import image_service

@worker.task()
async def process_uploaded_image(image_id: str) -> dict:
    """Process uploaded image: generate thumbnails, optimize, etc."""

    image = await ImageModel.get(image_id)
    if not image:
        return {"status": "error", "reason": "image_not_found"}

    # Download original
    original_bytes = await blob_service.download(image.blob_id)

    # Create variants
    thumbnail = await image_service.create_thumbnail(original_bytes)
    optimized = await image_service.optimize(original_bytes)

    # Upload variants
    thumb_blob = await blob_service.upload(thumbnail, f"thumbs/{image_id}.webp")
    opt_blob = await blob_service.upload(optimized, f"optimized/{image_id}.webp")

    # Update image record
    image.thumbnail_id = str(thumb_blob.id)
    image.optimized_id = str(opt_blob.id)
    await image.save()

    return {"status": "completed", "image_id": image_id}
```

### Cleanup Tasks

```python
# cleanup.py
from datetime import datetime, timedelta
from app.models.session import Session

@worker.task()
async def cleanup_expired_sessions() -> dict:
    """Remove expired sessions from database."""

    cutoff = datetime.now() - timedelta(days=30)

    expired = await Session.find(
        Session.expires_at < cutoff
    ).to_list()

    for session in expired:
        await session.delete()

    return {
        "status": "completed",
        "deleted_count": len(expired)
    }
```

### Chain Tasks

```python
@worker.task()
async def process_upload(file_id: str) -> dict:
    """Process file upload in stages."""

    # Stage 1: Validate
    validation = await validate_file.enqueue(file_id)
    result1 = await validation.result()

    if result1["valid"]:
        # Stage 2: Process
        processing = await process_file.enqueue(file_id)
        result2 = await processing.result()

        # Stage 3: Notify
        await notify_user.enqueue(file_id, "completed")

        return {"status": "completed", "stages": [result1, result2]}

    return {"status": "failed", "reason": "invalid_file"}
```

## Running the Worker

### Local Development

```bash
just worker-dev  # Start worker with auto-reload
```

### Docker

Workers are started automatically with `just dev` if enabled.

### Production

Workers run as separate processes/containers alongside the web server.

## Task Registration

**Critical**: Import task modules at the end of `worker.py`:

```python
# worker.py
from core.tasks.worker import worker

# ⚠️ Import task modules LAST so decorators can register
from . import emails  # noqa: E402, F401
from . import reports  # noqa: E402, F401
from . import processing  # noqa: E402, F401
from . import cleanup  # noqa: E402, F401
```

## Best Practices

1. **Keep tasks idempotent** - Same input should produce same output
2. **Handle failures gracefully** - Check if resources exist before accessing
3. **Return meaningful results** - Include status and relevant data
4. **Log important operations** - Use Python logging module
5. **Set appropriate timeouts** - Don't let tasks run forever
6. **Use retries for transient failures** - Network issues, rate limits
7. **Don't pass large objects** - Pass IDs and fetch from DB in task
8. **Monitor task queues** - Check for growing backlogs

## Error Handling

```python
import logging

logger = logging.getLogger(__name__)

@worker.task(max_retries=3)
async def risky_operation(data_id: str) -> dict:
    """Task that might fail."""
    try:
        # Fetch data
        data = await Data.get(data_id)
        if not data:
            logger.warning(f"Data not found: {data_id}")
            return {"status": "skipped", "reason": "not_found"}

        # Process
        result = await process_data(data)

        logger.info(f"Processed data: {data_id}")
        return {"status": "success", "result": result}

    except TransientError as e:
        # Retry on transient errors
        logger.error(f"Transient error processing {data_id}: {e}")
        raise  # Triggers retry

    except PermanentError as e:
        # Don't retry on permanent errors
        logger.error(f"Permanent error processing {data_id}: {e}")
        return {"status": "failed", "error": str(e)}
```

## Testing Tasks

```python
import pytest
from app.tasks.emails import send_welcome_email

@pytest.mark.asyncio
async def test_send_welcome_email(db, user):
    """Test welcome email task."""

    # Run task directly (not queued)
    result = await send_welcome_email(str(user.id))

    assert result["status"] == "sent"
    assert result["user_email"] == user.email

# For integration tests, use enqueue:
async def test_task_queue(db, user):
    task = await send_welcome_email.enqueue(str(user.id))
    result = await task.result(timeout=10)
    assert result["status"] == "sent"
```

## Task vs Service

**When to use tasks:**

- Operation takes >1 second
- User doesn't need immediate result
- Operation can fail and retry
- Scheduled/recurring work

**When to use services:**

- Immediate result needed
- Fast operation (<100ms)
- Synchronous validation
- Direct API calls

## Need Help?

- Core task changes: `https://github.com/alltuner/scaffolding`
- Streaq docs: Check Streaq documentation
- Async patterns: `https://docs.python.org/3/library/asyncio.html`
