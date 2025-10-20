# Core Services Module

**IMMUTABLE SCAFFOLDING CODE** - These are the framework's core services that provide essential functionality.

## What's Here

This module contains the scaffolding's core services:

- **email.py** - Email sending via AWS SES
- **blob.py** - File storage and blob management

## Important Rules

⚠️  **DO NOT MODIFY** these core services directly.

**For changes to core services:**

- File an issue at `https://github.com/alltuner/scaffolding`
- Core changes benefit all projects using the scaffolding

**For your application services:**

- Create them in `src/app/services/` instead
- Import core services when needed: `from vibetuner.services.email import send_email`

## User Service Pattern (for reference)

Your application services in `src/app/services/` should follow this pattern:

```python
from vibetuner.models import UserModel

class NotificationService:
    async def send_notification(
        self,
        user: UserModel,
        message: str,
        priority: str = "normal"
    ) -> bool:
        # Implementation
        return True

# Singleton
notification_service = NotificationService()
```

## Using Core Services

### Email Service

```python
from vibetuner.services.email import send_email

await send_email(
    to_email="user@example.com",
    subject="Welcome",
    html_content="<h1>Welcome!</h1>",
    text_content="Welcome!"
)
```

### Blob Service

```python
from vibetuner.services.blob import blob_service

# Upload file
blob = await blob_service.upload(file_data, "image.png")

# Get file URL
url = await blob_service.get_url(blob.id)
```

## Creating Your Own Services

Place your application services in `src/app/services/`:

```python
# src/app/services/external_api.py
import httpx

async def call_api(api_url: str, api_key: str, data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            api_url,
            json=data,
            headers={"Authorization": f"Bearer {api_key}"}
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
