# Core Services - DO NOT MODIFY

**⚠️ IMPORTANT**: These files are managed by the scaffolding system and
should NEVER be modified directly.

## Protected Core Services

- `email.py` - AWS SES email sending implementation
- `blob.py` - File storage and blob management

## Why These Files Are Protected

- Maintained by the scaffolding template
- Updates come through `just update-scaffolding`
- Manual changes will be lost on updates
- Core functionality that other parts depend on

## How to Extend Core Services

### Option 1: Wrapper Services

Create your own service that uses core services:

```python
# services/notifications.py
from .core.email import send_email

class NotificationService:
    async def send_welcome_email(self, user):
        # Add your custom logic
        await send_email(
            to_email=user.email,
            subject="Welcome!",
            html_content=render_template("welcome.html", {"user": user})
        )
```

### Option 2: Service Decorators

Enhance core services with decorators:

```python
# services/enhanced_email.py
from functools import wraps
from .core.email import send_email as core_send_email

async def send_email_with_tracking(*args, **kwargs):
    # Log email send
    await log_email_event("sending", kwargs.get("to_email"))
    
    # Call core service
    result = await core_send_email(*args, **kwargs)
    
    # Track completion
    await log_email_event("sent", kwargs.get("to_email"))
    return result
```

## If Core Services Are Insufficient

1. **Document the limitation** clearly
2. **Suggest to user**: "Core service missing feature X. Options:
   - Implement in application services layer
   - Use external service/library directly
   - Request scaffolding enhancement"
3. **Provide workaround** if possible

## Common Extension Patterns

### Email Service Extensions

```python
# services/email_extensions.py
from .core.email import send_email

async def send_templated_email(template_name: str, context: dict, to_email: str):
    """Send email using template system."""
    html = render_template(f"email/{template_name}.html", context)
    text = render_template(f"email/{template_name}.txt", context)
    
    await send_email(
        to_email=to_email,
        subject=context.get("subject", "Notification"),
        html_content=html,
        text_content=text
    )
```

### Blob Service Extensions

```python
# services/media.py
from .core.blob import BlobService

class MediaService(BlobService):
    async def upload_image(self, file, user_id: str):
        # Add image validation
        if not file.content_type.startswith("image/"):
            raise ValueError("Only images allowed")
        
        # Use core blob service
        return await self.upload(file, metadata={"user_id": user_id})
```

## Getting Help

If blocked by core service limitations:

1. Check if you can wrap/extend the service
2. Consider using the underlying libraries directly
3. Suggest the enhancement for the scaffolding
