# apps/wishlist/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("wishlists/",                          views.wishlist_view,        name="wishlist"),
    path("wishlist/toggle/<int:product_id>/",   views.toggle_wishlist,      name="toggle_wishlist"),
    path("wishlist/remove/<int:item_id>/",      views.remove_from_wishlist, name="remove_from_wishlist"),
    path("wishlist/move-to-cart/<int:item_id>/", views.move_to_cart,        name="move_to_cart"),
]