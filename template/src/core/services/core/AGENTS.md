# Core Services - DO NOT MODIFY

**⚠️ IMPORTANT**: Scaffolding-managed files. Changes will be lost on updates.

## Protected Files

- `email.py` - AWS SES email sending
- `blob.py` - File storage operations

## Extending Core Services

### Wrapper Services

```python
# services/notifications.py
from .core.email import send_email

class NotificationService:
    async def send_welcome_email(self, user):
        await send_email(
            to_email=user.email,
            subject="Welcome!",
            html_content=render_template("welcome.html", {"user": user})
        )
```

### Enhanced Services

```python
# services/enhanced_email.py
from .core.email import send_email as core_send_email

async def send_email_with_tracking(*args, **kwargs):
    await log_email_event("sending", kwargs.get("to_email"))
    result = await core_send_email(*args, **kwargs)
    await log_email_event("sent", kwargs.get("to_email"))
    return result
```

## If Core Is Insufficient

1. Wrap/extend the service
2. Use underlying libraries directly
3. Suggest enhancement to scaffolding repo
