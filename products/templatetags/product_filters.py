from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(int(key), 0)

@register.filter
def clean_wa(value):
    """Removes non-numeric characters for WhatsApp links."""
    if not value:
        return ""
    return "".join(filter(str.isdigit, str(value)))