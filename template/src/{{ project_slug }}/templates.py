from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ._paths import templates as default_template_path


class TemplateRenderer:
    """Modern Jinja template renderer with i18n support and fallback logic."""

    def __init__(self, template_path: Path | None = None):
        """Initialize the renderer with a base template path."""
        self.template_path = template_path or default_template_path
        self.env = Environment(  # noqa: S701
            loader=FileSystemLoader(self.template_path),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(
        self,
        template_name: str,
        context: Optional[Dict[str, Any]] = None,
        lang: Optional[str] = None,
    ) -> str:
        context = context or {}
        jinja_template_name = f"{template_name}.jinja"

        # Try localized template first if language is specified
        if lang:
            try:
                template = self.env.get_template(f"{lang}/{jinja_template_name}")
                return template.render(**context)
            except TemplateNotFound:
                pass  # Fall back to default template

        # Try default template
        try:
            template = self.env.get_template(f"default/{jinja_template_name}")
            return template.render(**context)
        except TemplateNotFound as err:
            raise TemplateNotFound(
                f"Template '{jinja_template_name}' not found. "
            ) from err


# Convenience function for one-off usage
def render_template(
    template_name: str,
    *,
    template_path: Path | None = None,
    context: Optional[Dict[str, Any]] = None,
    lang: Optional[str] = None,
) -> str:
    renderer = TemplateRenderer(template_path)
    return renderer.render(template_name, context, lang)
