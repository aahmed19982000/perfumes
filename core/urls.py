# core/urls.py

from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
import django.conf.urls.i18n as i18n

urlpatterns = [
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/",            admin.site.urls),

    # ── Apps — لازم "" مش "products" عشان الـ URLs تشتغل صح ──────
    path("", include("products.urls")),
    path("", include("accounts.urls")),
    path("", include("orders.urls")),
    path("", include("wishlist.urls")),
    path("", include("reviews.urls")),
    path('i18n/', include('django.conf.urls.i18n')),

    # ── الصفحة الرئيسية ──────────────────────────────────────────
    path("", views.home_view, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)