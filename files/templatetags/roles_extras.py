from django import template

register = template.Library()

@register.filter
def split_roles(value, sep=','):

    if not value:
        return []
    return [r.strip() for r in value.split(sep) if r.strip()]



@register.filter
def endswith(value, suffix):
    if not isinstance(value, str):
        return False
    return value.lower().endswith(str(suffix).lower())
