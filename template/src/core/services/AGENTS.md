# Services Module

Business logic and external service integrations.

## Quick Reference

**Add your services**: Create files in `services/` (e.g., `notifications.py`)
**Core services** (DO NOT MODIFY): `core/email.py`, `core/blob.py`

## Service Pattern

```python
from ..models import User
from ..core.config import settings

class NotificationService:
    async def send_notification(
        self,
        user: User,
        message: str,
        priority: str = "normal"
    ) -> bool:
        # Implementation
        return True

# Singleton
notification_service = NotificationService()
```

## Using Core Services

### Email

```python
from .core.email import send_email

await send_email(
    to_email="user@example.com",
    subject="Welcome",
    html_content="<h1>Welcome!</h1>",
    text_content="Welcome!"
)
```

### External APIs

```python
import httpx

async def call_api(data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.API_URL,
            json=data,
            headers={"Authorization": f"Bearer {settings.API_KEY}"}
        )
        response.raise_for_status()
        return response.json()
```

## Dependency Injection

```python
from fastapi import Depends

@router.post("/notify")
async def notify(
    message: str,
    service=Depends(lambda: notification_service)
):
    await service.send_notification(user, message)
```
