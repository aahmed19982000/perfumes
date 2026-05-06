# apps/orders/urls.py  —  أضف للملف الموجود

from django.urls import path
from . import views

urlpatterns = [
    # السلة
    path("shop-cart/",                   views.cart_view,         name="cart"),
    path("cart/add/<int:product_id>/",   views.add_to_cart,       name="add_to_cart"),
    path("cart/update/<int:item_id>/",   views.update_cart,       name="update_cart"),
    path("cart/remove/<int:item_id>/",   views.remove_from_cart,  name="remove_from_cart"),

    # الطلبات
    path("checkout/",                    views.checkout_view,     name="checkout"),
    path("order/success/<str:order_number>/", views.order_success_view, name="order_success"),
    path("orders/",                      views.order_list_view,   name="order_list"),
    path("orders/<str:order_number>/",   views.order_detail_view, name="order_detail"),
    path("orders/<str:order_number>/cancel/", views.cancel_order_view, name="cancel_order"),
    path("track-order/",                 views.track_order_view,  name="track_order"),
]