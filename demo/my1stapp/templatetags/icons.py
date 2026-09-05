from django import template

register = template.Library()


@register.inclusion_tag("components/icon.html")
def icon(name, size=24):
    return {
        "name": name,
        "size": size,
    }
