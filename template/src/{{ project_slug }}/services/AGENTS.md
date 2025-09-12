
# Services Module

Business logic and external service integrations.

## Structure

**Add your services here:**

- Create files directly in `services/` (e.g., `notifications.py`, `payments.py`)

**Core services (DO NOT MODIFY):**

- `core/email.py` - AWS SES email sending
- `core/blob.py` - File storage operations

## Service Pattern

```python
from typing import Optional
from ..models import User
from ..core.config import settings

class NotificationService:
    async def send_notification(
        self, 
        user: User, 
        message: str,
        priority: str = "normal"
    ) -> bool:
        """Send notification to user."""
        # Implementation here
        return True

# Singleton instance
notification_service = NotificationService()
```

## Email Service

Using the core email service:

```python
from .core.email import send_email

await send_email(
    to_email="user@example.com",
    subject="Welcome",
    html_content="<h1>Welcome!</h1>",
    text_content="Welcome!"
)
```

## External APIs

```python
import httpx
from ..core.config import settings

async def call_external_api(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.EXTERNAL_API_URL,
            json=data,
            headers={"Authorization": f"Bearer {settings.API_KEY}"}
        )
        response.raise_for_status()
        return response.json()
```

## Dependency Injection

Use in routes:

```python
from fastapi import Depends
from ..services.notifications import notification_service

@router.post("/notify")
async def notify(
    message: str,
    service: NotificationService = Depends(lambda: notification_service)
):
    await service.send_notification(user, message)
```

## Package Management

```bash
uv add httpx boto3          # Add service dependencies
uv sync                     # Sync all dependencies
```
