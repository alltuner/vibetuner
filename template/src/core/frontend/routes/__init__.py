from fastapi import Request


def get_homepage_url(request: Request, path_only: bool = True) -> str:
    """Get homepage URL for the current language."""
    try:
        url = request.url_for("homepage", lang=request.state.language)
    except Exception:
        # Fallback to default language if the requested language is not available
        url = request.url_for("homepage")

    return url.path if path_only else str(url)
