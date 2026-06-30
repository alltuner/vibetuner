from urllib.parse import urlsplit

from fastapi import Request


def get_homepage_url(request: Request, path_only: bool = True) -> str:
    """Get homepage URL for the current language."""
    try:
        url = request.url_for("homepage", lang=request.state.language)
    except Exception:
        # Fallback to default language if the requested language is not available
        url = request.url_for("homepage")

    return url.path if path_only else str(url)


def is_safe_redirect(url: str | None) -> bool:
    """Return True only for same-origin relative paths safe to redirect to.

    Guards post-auth redirect targets that originate from user input
    (``?next=``, ``current``) against open-redirect attacks. A safe value
    is a single-leading-slash path with no scheme and no network location,
    so ``https://evil.com``, ``//evil.com`` (protocol-relative) and
    ``javascript:`` URLs are all rejected. Backslashes are treated as
    slashes because some browsers normalise them, so ``/\\evil.com`` is
    rejected too.
    """
    if not url:
        return False

    normalized = url.replace("\\", "/")
    if not normalized.startswith("/") or normalized.startswith("//"):
        return False

    parts = urlsplit(normalized)
    return not parts.scheme and not parts.netloc
