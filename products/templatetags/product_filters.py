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

@register.filter
def messenger_chat(value):
    """Converts a Facebook/Messenger link to a mobile-friendly chat link."""
    if not value:
        return "#"
    # Extract username from URL
    username = str(value).rstrip('/').split('/')[-1]
    # Ensure it uses the messenger.com format which is more reliable on mobile
    return f"https://www.messenger.com/t/{username}"