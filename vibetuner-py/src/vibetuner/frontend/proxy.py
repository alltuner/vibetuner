# ABOUTME: ASGI app wrapper that processes X-Forwarded-For and X-Forwarded-Proto headers
# ABOUTME: Uses Granian's proxy header support to extract real client IP and protocol
from granian.utils.proxies import wrap_asgi_with_proxy_headers

from vibetuner.config import settings
from vibetuner.frontend import app as _app


# Wrap the FastAPI app with Granian's proxy header processor
# This enables real client IP detection when behind reverse proxies (nginx, Cloudflare, etc.)
# Only headers from trusted_proxy_hosts will be processed to prevent IP spoofing
app = wrap_asgi_with_proxy_headers(
    _app, trusted_hosts=settings.trusted_proxy_hosts_list
)
