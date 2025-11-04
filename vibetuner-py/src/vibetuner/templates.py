from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from . import paths


def _get_base_paths_for_namespace(
    namespace: str | None,
    template_path: Path | list[Path] | None,
) -> list[Path]:
    """Get base template paths based on namespace and template_path."""
    if template_path is not None:
        return [template_path] if isinstance(template_path, Path) else template_path

    # Map known namespaces to their predefined paths
    if namespace == "email":
        return paths.email_templates
    if namespace == "markdown":
        return paths.markdown_templates
    if namespace == "frontend":
        return paths.frontend_templates

    # Default for unknown or None namespace
    # Only include app_templates if project root has been set
    path_list = []
    if paths.app_templates is not None:
        path_list.append(paths.app_templates)
    path_list.append(paths.core_templates)
    return path_list


def _build_search_paths(
    base_paths: list[Path],
    namespace: str | None,
    template_path: Path | list[Path] | None,
) -> list[Path]:
    """Build list of directories to search for templates."""
    search_paths: list[Path] = []
    known_namespaces = ("email", "markdown", "frontend")

    for base_path in base_paths:
        # If namespace is known and we're using default paths, they already include it
        if namespace in known_namespaces and template_path is None:
            if base_path.is_dir():
                search_paths.append(base_path)
        elif namespace:
            # Append namespace to path for custom namespaces or explicit paths
            ns_path = base_path / namespace
            if ns_path.is_dir():
                search_paths.append(ns_path)
        else:
            if base_path.is_dir():
                search_paths.append(base_path)

    return search_paths


def _render_template_with_env(
    env: Environment,
    jinja_template_name: str,
    lang: str | None,
    context: dict[str, Any],
) -> str:
    """Render template using Jinja environment with language fallback."""
    # Try language-specific folder first
    if lang:
        try:
            template = env.get_template(f"{lang}/{jinja_template_name}")
            return template.render(**context)
        except TemplateNotFound:
            pass

    # Fallback to default folder
    template = env.get_template(f"default/{jinja_template_name}")
    return template.render(**context)


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
            collections. When a list is provided, searches in order (project templates
            override package templates). Defaults to the package's bundled templates.
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

    context = context or {}

    # Determine base paths from namespace and template_path
    base_paths = _get_base_paths_for_namespace(namespace, template_path)

    # Build search paths from base paths
    search_paths = _build_search_paths(base_paths, namespace, template_path)

    if not search_paths:
        raise TemplateNotFound(
            f"No valid template paths found for namespace '{namespace}'"
        )

    # Create Jinja environment with search paths
    env = Environment(  # noqa: S701
        loader=FileSystemLoader(search_paths),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Render template with language fallback
    jinja_template_name = f"{template_name}.jinja"
    try:
        return _render_template_with_env(env, jinja_template_name, lang, context)
    except TemplateNotFound as err:
        raise TemplateNotFound(
            f"Template '{jinja_template_name}' not found under '{search_paths}'."
        ) from err
