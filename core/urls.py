# core/urls.py

from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from products.sitemaps import ProductSitemap, CategorySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
}

from django.views.generic import TemplateView

urlpatterns = [
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("manage-perfumes/", include("backend.urls")),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/",            admin.site.urls),

    # ── Apps — لازم "" مش "products" عشان الـ URLs تشتغل صح ──────
    path("", include("products.urls")),
    path("", include("accounts.urls")),
    path("", include("orders.urls")),
    path("", include("wishlist.urls")),
    path("", include("reviews.urls")),
    path("", include("contact.urls")),
    path('i18n/', include('django.conf.urls.i18n')),

    # ── الصفحة الرئيسية ──────────────────────────────────────────
    path("", views.home_view, name="home"),
    
    # ── الصفحات الثابتة ──────────────────────────────────────────
    path("about/",   views.about_view,   name="about"),
    path("faq/",     views.faq_view,     name="faq"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("terms/",   views.terms_view,   name="terms"),
    path("offers/",  views.offers_view,  name="offers"),
    path("brands/",  views.brands_view,  name="brands"),
]

from django.urls import re_path
from django.views.static import serve
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]