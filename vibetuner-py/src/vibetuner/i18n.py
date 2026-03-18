# ABOUTME: i18n facade that delegates to starlette-babel when available.
# ABOUTME: Provides noop fallbacks for gettext_lazy/ngettext when [i18n] is not installed.
from vibetuner.extras import has_extra


if has_extra("i18n"):
    from starlette_babel import gettext_lazy
else:

    def gettext_lazy(message: str, *args: str, **kwargs) -> str:  # type: ignore[misc]
        """Noop translation: returns the first argument unchanged.

        Handles both gettext(msg) and ngettext(singular, plural, n) calling
        conventions. For ngettext, returns singular when n==1, plural otherwise.
        """
        if args and len(args) >= 2:
            # ngettext(singular, plural, n) pattern
            plural, n = args[0], args[1]
            return message if n == 1 else plural
        return message
