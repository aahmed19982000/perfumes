import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.models import HeaderSettings

settings = HeaderSettings.load()
print(f"Logo Text: {settings.logo_text}")
print(f"Logo Image: {settings.logo_image}")
print(f"Logo Image URL: {settings.logo_image.url if settings.logo_image else 'None'}")
