# products/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("products/",            views.product_list,   name="products"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]