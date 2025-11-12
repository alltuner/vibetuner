# Services Module Development

Core services for the vibetuner framework. This guide is for **developers working on the framework**,
not end users.

## Module Structure

```text
services/
├── email.py    # Email sending via AWS SES
└── blob.py     # File storage and blob management
```

## Key Services

### Email Service (email.py)

Handles email sending via AWS SES:

```python
async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str | None = None,
    from_email: str | None = None,
) -> None:
    # Implementation using aioboto3 SES
```

**Key features:**

- Async email sending via AWS SES
- HTML and plain text support
- Configurable sender address
- Error handling and logging

**Used by:**

- Magic link authentication
- Password reset flows
- User notifications
- Background job email tasks

### Blob Service (blob.py)

File storage management (S3 or local):

```python
class BlobService:
    async def upload(self, file_data: bytes, filename: str) -> Blob
    async def download(self, blob_id: str) -> bytes
    async def delete(self, blob_id: str) -> None
    async def get_url(self, blob_id: str, expires_in: int = 3600) -> str
```

**Key features:**

- S3 storage with local fallback
- Presigned URL generation
- File metadata tracking via Blob model
- Async operations

## Development Guidelines

### Adding New Core Services

When adding services to the framework:

1. **Consider scope**: Should this be in the framework or user code?
2. **Use async**: All service methods should be async
3. **Error handling**: Use try/except with proper logging
4. **Configuration**: Use settings from `vibetuner.config`
5. **Documentation**: Add docstrings and type hints

### Modifying Existing Services

When changing core services:

1. **Backward compatibility**: Don't break existing user code
2. **Test thoroughly**: Services are used across many projects
3. **Update type hints**: Keep annotations current
4. **Document changes**: Update docstrings and CHANGELOG
5. **Consider security**: Email and storage are security-sensitive

## Testing

Test service changes by scaffolding and running a project:

```bash
cd /Users/dpoblador/repos/vibetuner
uv run --directory vibetuner-py vibetuner scaffold new /tmp/test --defaults
cd /tmp/test
just dev
```

Test scenarios:

1. **Email**: Send test emails, verify delivery
2. **Blob storage**: Upload, download, delete files
3. **Error cases**: Network failures, invalid input
4. **Configuration**: Test with different settings
5. **Integration**: Test from routes and tasks

## Common Pitfalls

### Email Service

- **AWS credentials**: Ensure proper IAM permissions
- **Rate limiting**: SES has sending limits
- **Bounces**: Handle bounce notifications properly
- **HTML sanitization**: Don't trust user HTML

### Blob Service

- **File size**: Large files need streaming
- **Security**: Validate file types and content
- **Storage costs**: Monitor S3 usage
- **Cleanup**: Delete unused blobs

### General

- **Async context**: Services run in async context
- **Connection pooling**: Reuse HTTP clients
- **Configuration**: Read from settings, not hardcode
- **Logging**: Use loguru for consistent logging

## Related Files

- `vibetuner/config.py` - Service configuration
- `vibetuner/models/blob.py` - Blob metadata model
- `vibetuner/frontend/email.py` - Magic link email handling
