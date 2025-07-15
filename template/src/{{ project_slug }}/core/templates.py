from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .paths import templates as default_template_path


def render_static_template(
    template_name: str,
    *,
    template_path: Path | None = None,
    namespace: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    lang: Optional[str] = None,
) -> str:
    """Render a Jinja template with optional i18n and namespace support.

    This simplified functional helper replaces the old ``TemplateRenderer``
    class while adding **namespace** awareness:

    1. Optionally switch to *template_path / namespace* if that directory
       exists, letting you segment templates per tenant, brand, or feature
       module without changing call‑sites.
    2. Within the selected base directory attempt ``<lang>/<name>.jinja``
       when *lang* is provided.
    3. Fallback to ``default/<name>.jinja``.

    Args:
        template_name: Base filename without extension (e.g. ``"invoice"``).
        template_path: Root directory containing template collections. Defaults
            to the library's built‑in path if omitted.
        namespace: Optional subfolder under *template_path* to confine the
            lookup. Ignored when the directory does not exist.
        context: Variables passed to the template while rendering.
        lang: Language code such as ``"en"`` or ``"es"`` for localized
            templates.

    Returns:
        The rendered template as a string.

    Raises:
        TemplateNotFound: When no suitable template could be located after all
            fallbacks.
    """

    # 0. Normalise inputs
    context = context or {}
    base_path = template_path or default_template_path

    # 1. Apply namespace if requested and actually present on disk
    if namespace:
        ns_path = base_path / namespace
        if ns_path.is_dir():
            base_path = ns_path

    # 2. Prepare Jinja environment rooted at *base_path*
    env = Environment(  # noqa: S701
        loader=FileSystemLoader(base_path),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    jinja_template_name = f"{template_name}.jinja"

    # 3. Try language‑specific folder first
    if lang:
        try:
            template = env.get_template(f"{lang}/{jinja_template_name}")
            return template.render(**context)
        except TemplateNotFound:
            # Missing locale template – fall through to default lookup
            pass

    # 4. Default folder fallback
    try:
        template = env.get_template(f"default/{jinja_template_name}")
        return template.render(**context)
    except TemplateNotFound as err:
        raise TemplateNotFound(
            f"Template '{jinja_template_name}' not found under '{base_path}'."
        ) from err
