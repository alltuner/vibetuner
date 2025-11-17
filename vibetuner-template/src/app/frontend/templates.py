# ABOUTME: Custom Jinja2 template filters for the application.
# ABOUTME: Register filters using the @register_filter() decorator.

from vibetuner.frontend.templates import register_filter


# Example custom filters - remove or modify as needed
@register_filter()
def uppercase(value):
    """Convert value to uppercase.

    Usage in templates:
        {{ user.name | uppercase }}
    """
    return str(value).upper()


@register_filter("money")
def format_money(value):
    """Format value as USD currency.

    Usage in templates:
        {{ product.price | money }}
    """
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)
