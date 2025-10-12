# Application Services

**YOUR BUSINESS LOGIC GOES HERE** - Encapsulate complex operations and external integrations.

## What Goes Here

Create your application-specific services in this directory:

- Third-party API integrations (Stripe, SendGrid, Twilio, etc.)
- Complex business logic
- Data processing pipelines
- Notification systems
- Report generators
- Any reusable logic that doesn't belong in routes or models

## Service Pattern

```python
# notifications.py
from core.models import UserModel
from core.services.email import send_email
from app.config import settings

class NotificationService:
    """Handle all notification delivery."""

    async def send_welcome_email(self, user: UserModel) -> bool:
        """Send welcome email to new user."""
        await send_email(
            to_email=user.email,
            subject=f"Welcome to {settings.project_name}!",
            html_content=f"<h1>Welcome {user.display_name}!</h1>",
            text_content=f"Welcome {user.display_name}!"
        )
        return True

    async def notify_admin(self, message: str, severity: str = "info") -> None:
        """Send notification to admin."""
        # Implementation
        pass

# Singleton instance
notification_service = NotificationService()
```

## Available from Core

### Email Service

```python
from core.services.email import send_email

await send_email(
    to_email="user@example.com",
    subject="Your Subject",
    html_content="<p>HTML version</p>",
    text_content="Plain text version"
)
```

### Blob Storage Service

```python
from core.services.blob import blob_service

# Upload file
blob = await blob_service.upload(file_bytes, filename="document.pdf")

# Get URL
url = await blob_service.get_url(blob.id)

# Delete
await blob_service.delete(blob.id)
```

## Common Patterns

### External API Integration

```python
# payment.py
import httpx
from app.config import settings

class PaymentService:
    """Stripe payment integration."""

    def __init__(self):
        self.api_key = settings.stripe_api_key
        self.base_url = "https://api.stripe.com/v1"

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd"
    ) -> dict:
        """Create a Stripe payment intent."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/payment_intents",
                auth=(self.api_key.get_secret_value(), ""),
                data={"amount": amount, "currency": currency}
            )
            response.raise_for_status()
            return response.json()

    async def retrieve_payment(self, payment_id: str) -> dict:
        """Get payment status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payment_intents/{payment_id}",
                auth=(self.api_key.get_secret_value(), "")
            )
            response.raise_for_status()
            return response.json()

payment_service = PaymentService()
```

### Data Processing Service

```python
# analytics.py
from datetime import datetime, timedelta
from app.models.event import Event

class AnalyticsService:
    """Process and aggregate analytics data."""

    async def get_daily_stats(self, days: int = 7) -> dict:
        """Get aggregated stats for past N days."""
        start_date = datetime.now() - timedelta(days=days)

        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "count": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"}
            }},
            {"$sort": {"_id": 1}}
        ]

        results = await Event.aggregate(pipeline).to_list()
        return {
            "dates": [r["_id"] for r in results],
            "counts": [r["count"] for r in results],
            "unique_users": [len(r["unique_users"]) for r in results]
        }

analytics_service = AnalyticsService()
```

### File Processing Service

```python
# document.py
from io import BytesIO
from PIL import Image
from core.services.blob import blob_service

class DocumentService:
    """Process uploaded documents."""

    async def process_image(
        self,
        file_bytes: bytes,
        filename: str
    ) -> dict:
        """Process and optimize uploaded image."""
        # Open image
        img = Image.open(BytesIO(file_bytes))

        # Create thumbnail
        thumb = img.copy()
        thumb.thumbnail((300, 300))

        # Save optimized versions
        optimized = BytesIO()
        img.save(optimized, format="WEBP", quality=85)

        thumb_bytes = BytesIO()
        thumb.save(thumb_bytes, format="WEBP", quality=85)

        # Upload to blob storage
        original = await blob_service.upload(
            optimized.getvalue(),
            f"images/{filename}.webp"
        )
        thumbnail = await blob_service.upload(
            thumb_bytes.getvalue(),
            f"thumbnails/{filename}.webp"
        )

        return {
            "original_id": str(original.id),
            "thumbnail_id": str(thumbnail.id),
            "dimensions": img.size
        }

document_service = DocumentService()
```

### Background Task Orchestration

```python
# orchestrator.py
from app.tasks.email import send_digest_email
from app.tasks.cleanup import cleanup_old_files

class TaskOrchestrator:
    """Coordinate multiple background tasks."""

    async def run_daily_maintenance(self) -> dict:
        """Run all daily maintenance tasks."""
        results = {}

        # Cleanup old files
        cleanup_task = await cleanup_old_files.enqueue()
        results["cleanup"] = cleanup_task.id

        # Send digest emails
        digest_task = await send_digest_email.enqueue()
        results["digest"] = digest_task.id

        return results

orchestrator = TaskOrchestrator()
```

## Dependency Injection

Use services in routes with FastAPI's dependency injection:

```python
# routes/payments.py
from fastapi import APIRouter, Depends
from app.services.payment import payment_service, PaymentService

router = APIRouter()

def get_payment_service() -> PaymentService:
    return payment_service

@router.post("/create-payment")
async def create_payment(
    amount: int,
    service: PaymentService = Depends(get_payment_service)
):
    intent = await service.create_payment_intent(amount)
    return {"client_secret": intent["client_secret"]}
```

## Service Organization

### Single Responsibility

Each service should have a focused purpose:

```text
services/
├── __init__.py
├── payment.py         # Payment processing
├── email.py           # Email notifications (custom, not core)
├── sms.py             # SMS notifications
├── analytics.py       # Data analytics
├── export.py          # Report exports
└── integration/       # Complex integrations
    ├── __init__.py
    ├── crm.py
    └── inventory.py
```

### Service Factory Pattern

For services that need configuration:

```python
# factory.py
from app.config import settings

class ServiceFactory:
    """Factory for creating configured service instances."""

    @staticmethod
    def create_payment_service():
        if settings.payment_provider == "stripe":
            from .payment.stripe import StripeService
            return StripeService(settings.stripe_api_key)
        elif settings.payment_provider == "paypal":
            from .payment.paypal import PayPalService
            return PayPalService(settings.paypal_api_key)
        raise ValueError(f"Unknown provider: {settings.payment_provider}")

payment_service = ServiceFactory.create_payment_service()
```

## Testing Services

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.payment import PaymentService

@pytest.fixture
def payment_service():
    return PaymentService()

async def test_create_payment_intent(payment_service):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "id": "pi_123",
            "client_secret": "secret_123"
        }

        result = await payment_service.create_payment_intent(1000)

        assert result["id"] == "pi_123"
        mock_post.assert_called_once()
```

## Error Handling

```python
# exceptions.py
class ServiceError(Exception):
    """Base exception for service errors."""
    pass

class ExternalAPIError(ServiceError):
    """External API returned an error."""
    pass

class RateLimitError(ServiceError):
    """Rate limit exceeded."""
    pass

# In service:
async def call_api(self) -> dict:
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise RateLimitError("API rate limit exceeded")
        raise ExternalAPIError(f"API error: {e}")
```

## Best Practices

1. **Keep services stateless** - Don't store mutable state in service instances
2. **Use dependency injection** - Pass dependencies to constructors or methods
3. **Handle errors gracefully** - Wrap external calls in try/except
4. **Log important operations** - Use Python's logging module
5. **Use async/await** - Keep the async chain unbroken
6. **Type everything** - Use type hints for all parameters and returns
7. **Document methods** - Add docstrings explaining purpose and parameters
8. **Test thoroughly** - Mock external dependencies in tests

## Configuration

Add service configuration to `app/config.py`:

```python
class Configuration(BaseSettings):
    # Payment
    stripe_api_key: SecretStr | None = None
    payment_provider: str = "stripe"

    # Email (if not using core)
    sendgrid_api_key: SecretStr | None = None

    # SMS
    twilio_account_sid: str | None = None
    twilio_auth_token: SecretStr | None = None

    # External APIs
    api_timeout: int = 30
    api_retry_attempts: int = 3
```

## Need Help?

- Core service changes: `https://github.com/alltuner/scaffolding`
- httpx docs: `https://www.python-httpx.org/`
- FastAPI dependency injection: `https://fastapi.tiangolo.com/tutorial/dependencies/`
