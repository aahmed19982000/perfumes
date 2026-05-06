# core/admin.py

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html


# ── تخصيص عنوان لوحة الإدارة ─────────────────────────────────────
admin.site.site_header  = "لوحة تحكم Mava"
admin.site.site_title   = "Mava Admin"
admin.site.index_title  = "مرحباً بك في لوحة التحكم"