from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .paths import (
    app_templates,
    core_templates,
    email_templates,
    frontend_templates,
    markdown_templates,
    templates,
)


def render_static_template(
    template_name: str,
    *,
    template_path: Path | list[Path] | None = None,
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
        template_path: Root directory or list of directories containing template 
            collections. When a list is provided, searches in order (app overrides 
            come first). Defaults to the library's built‑in path if omitted.
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
    
    # Ensure we have a list of paths, with smart namespace handling
    if template_path is None:
        # No template_path provided - use namespace to determine paths
        if namespace == "email":
            base_paths = email_templates
        elif namespace == "markdown":
            base_paths = markdown_templates
        elif namespace == "frontend":
            base_paths = frontend_templates
        else:
            # Unknown namespace, use root templates with namespace subfolder
            base_paths = [app_templates, core_templates]
    elif isinstance(template_path, Path):
        base_paths = [template_path]
    else:
        base_paths = template_path

    # 1. Apply namespace if requested and collect valid paths
    search_paths: list[Path] = []
    for base_path in base_paths:
        # If namespace matches known template types, paths already point to correct location
        if namespace in ("email", "markdown", "frontend") and template_path is None:
            # Paths already include the namespace, don't append it again
            if base_path.is_dir():
                search_paths.append(base_path)
        elif namespace:
            # For other namespaces or when template_path is explicitly provided
            ns_path = base_path / namespace
            if ns_path.is_dir():
                search_paths.append(ns_path)
        else:
            if base_path.is_dir():
                search_paths.append(base_path)

    if not search_paths:
        raise TemplateNotFound(
            f"No valid template paths found for namespace '{namespace}'"
        )

    # 2. Prepare Jinja environment with multiple search paths
    env = Environment(  # noqa: S701
        loader=FileSystemLoader(search_paths),
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
            f"Template '{jinja_template_name}' not found under '{search_paths}'."
        ) from err
