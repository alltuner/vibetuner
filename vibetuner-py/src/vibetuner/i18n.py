# ABOUTME: Public i18n primitives — locale resolver registry, request-language helper, language picker
# ABOUTME: Used by apps that need to override the locale chain or expose a language switcher
"""Public i18n primitives for vibetuner apps.

Three pieces of glue that close the gap between vibetuner's
:class:`~starlette_babel.LocaleMiddleware` setup and per-tenant /
user-driven language flows:

* :func:`register_locale_resolver` — inject a custom selector into the
  locale-detection chain (e.g. "this tenant always renders in its own
  language regardless of ``Accept-Language``").
* :func:`set_request_language` — update both the Babel context and
  ``request.state.language`` in one call so ``{% trans %}``, the
  ``<html lang>`` attribute and the ``Content-Language`` header all
  agree.
* :func:`language_picker` — produce ``[{code, name}]`` for a language
  switcher, with names rendered in the *current* display locale (not
  hard-coded to English).

``language_picker`` is also exposed as a Jinja global so templates can
call it directly — no new context variable, no override of the existing
``supported_languages`` template var (which stays a ``set[str]`` of
codes).
"""

from collections.abc import Callable

from babel import Locale, UnknownLocaleError
from fastapi.requests import HTTPConnection
from starlette.requests import Request
from starlette_babel import get_locale, set_locale

from vibetuner.context import ctx
from vibetuner.logging import logger


__all__ = [
    "LocaleResolver",
    "combined_locale_selector",
    "get_locale_resolvers",
    "language_picker",
    "register_locale_resolver",
    "set_request_language",
]


LocaleResolver = Callable[[HTTPConnection], str | None]


_resolvers: list[tuple[int, int, LocaleResolver]] = []
_insertion_counter = 0


def register_locale_resolver(
    resolver: LocaleResolver,
    *,
    priority: int = 0,
) -> LocaleResolver:
    """Register a custom locale resolver at the front of the selector chain.

    Resolvers receive the current
    :class:`~fastapi.requests.HTTPConnection` and return either a
    locale code (e.g. ``"ca"``) or ``None`` to defer to the next
    resolver. The first resolver to return a non-``None`` value wins.

    All registered resolvers run *before* vibetuner's built-in
    selectors (query param, URL prefix, user session, cookie,
    ``Accept-Language``). Within the registered group, resolvers are
    ordered by ``priority`` ascending — lower numbers run first. Ties
    fall back to insertion order.

    The combined selector is fail-soft: if a resolver raises, the
    exception is logged and the next resolver runs. This avoids
    turning a misbehaving per-tenant lookup into a 500.

    Args:
        resolver: Callable that takes an ``HTTPConnection`` and returns
            ``str | None``. Must be synchronous; do any I/O upstream.
        priority: Sort key within the registered group. Lower runs
            first. Defaults to ``0``.

    Returns:
        The resolver, unchanged — handy for use as a decorator.

    Example::

        from vibetuner.i18n import register_locale_resolver

        def tenant_locale(conn):
            tenant = conn.scope.get("state", {}).get("tenant")
            return tenant.language if tenant else None

        register_locale_resolver(tenant_locale)
    """
    if not callable(resolver):
        raise TypeError(
            f"register_locale_resolver: expected callable, got {type(resolver).__name__}"
        )
    global _insertion_counter
    _resolvers.append((priority, _insertion_counter, resolver))
    _insertion_counter += 1
    _resolvers.sort(key=lambda item: (item[0], item[1]))
    return resolver


def get_locale_resolvers() -> list[LocaleResolver]:
    """Return registered locale resolvers in chain order."""
    return [resolver for _, _, resolver in _resolvers]


def combined_locale_selector(conn: HTTPConnection) -> str | None:
    """Run registered resolvers in priority order; return the first hit.

    This is the single selector vibetuner inserts into
    :class:`~starlette_babel.LocaleMiddleware` to delegate to
    user-registered resolvers. Apps usually do not call it directly.
    """
    for resolver in get_locale_resolvers():
        try:
            result = resolver(conn)
        except Exception as exc:
            logger.error(
                f"locale resolver {getattr(resolver, '__name__', resolver)!r} raised {exc!r}"
            )
            continue
        if result:
            return result
    return None


def _reset_locale_resolvers() -> None:
    """Test hook: clear the resolver registry."""
    global _insertion_counter
    _resolvers.clear()
    _insertion_counter = 0


def set_request_language(request: Request, code: str) -> None:
    """Force the active language for the rest of the request.

    Updates both the Babel context (drives ``{% trans %}``) and
    ``request.state.language`` (drives ``<html lang>`` and the
    ``Content-Language`` response header) so all three stay in sync.

    The code is normalized to lowercase and validated with
    :func:`babel.Locale.parse`; an invalid code raises
    :class:`ValueError` rather than letting Babel surface a less
    helpful error later in the request.

    Use this for the late-bound case — e.g. switching to the user's
    preferred language right after a session login. For the
    "every request for tenant X uses language Y" case, prefer
    :func:`register_locale_resolver`.

    Args:
        request: The active Starlette/FastAPI request.
        code: Two-letter language code (e.g. ``"ca"``).

    Raises:
        TypeError: If ``code`` is not a string.
        ValueError: If ``code`` is not a parseable locale.
    """
    if not isinstance(code, str):
        raise TypeError(
            f"set_request_language: code must be str, got {type(code).__name__}"
        )
    normalized = code.lower()
    try:
        locale = Locale.parse(normalized)
    except (UnknownLocaleError, ValueError) as exc:
        raise ValueError(
            f"set_request_language: {code!r} is not a valid locale code"
        ) from exc
    set_locale(locale)
    request.state.language = normalized


def language_picker(
    display_locale: str | Locale | None = None,
    *,
    supported_languages: set[str] | None = None,
) -> list[dict[str, str]]:
    """Return a sorted ``[{code, name}, ...]`` list for a language switcher.

    Names are rendered in ``display_locale`` so the dropdown shows
    itself in the user's current language. Browsing in Spanish gives
    "inglés / español / catalán"; browsing in Catalan gives
    "anglès / espanyol / català". When ``display_locale`` is omitted,
    the current Babel context locale is used (falls back to the
    project's default language).

    Args:
        display_locale: Locale used to render display names. Accepts a
            string code or a :class:`babel.Locale`. Defaults to the
            current request's locale.
        supported_languages: Override the set of language codes to
            include. Defaults to ``settings.project.languages``.

    Returns:
        A list of ``{"code": "<xx>", "name": "<localized name>"}``
        dicts, sorted by ``name``.
    """
    languages = (
        supported_languages
        if supported_languages is not None
        else ctx.supported_languages
    )

    if display_locale is None:
        try:
            display = get_locale()
        except Exception:
            display = Locale.parse(ctx.default_language)
    elif isinstance(display_locale, Locale):
        display = display_locale
    else:
        display = Locale.parse(display_locale)

    entries: list[dict[str, str]] = []
    for code in languages:
        try:
            locale = Locale.parse(code)
            name = locale.get_display_name(display) or code
        except Exception:
            name = code
        entries.append({"code": code, "name": name})

    entries.sort(key=lambda entry: entry["name"].casefold())
    return entries
