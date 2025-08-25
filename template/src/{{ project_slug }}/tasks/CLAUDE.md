# Tasks Module

Background job processing with Redis and Streaq (when enabled).

## Setup

Only available when job queue is enabled during scaffolding.

## Task Pattern

```python
from streaq import task
from ..models import User

@task
async def send_welcome_email(user_id: str):
    """Send welcome email to new user."""
    user = await User.get(user_id)
    if user:
        # Send email logic here
        return {"status": "sent", "user": user.email}
```

## Queueing Tasks

From routes:

```python
from fastapi import Depends
from ..frontend.deps import get_streaq_client
from ..tasks import send_welcome_email

@router.post("/signup")
async def signup(
    email: str,
    streaq=Depends(get_streaq_client)
):
    user = await create_user(email)
    await streaq.enqueue(send_welcome_email, user.id)
    return {"status": "registered"}
```

## Worker Management

```bash
# Development
just worker-dev             # Run worker locally

# Production
docker compose up worker    # Run worker in Docker
```

## Task Configuration

In `worker.py`:

```python
from streaq import Streaq
from ..core.config import settings

streaq = Streaq(redis_url=settings.REDIS_URL)

# Register tasks
streaq.task(send_welcome_email)
streaq.task(process_payment)
```

## Monitoring

Check Redis for job status:

```python
job_id = await streaq.enqueue(my_task, arg1, arg2)
status = await streaq.get_job_status(job_id)
result = await streaq.get_job_result(job_id)
```
