# apps/reviews/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("reviews/add/<int:product_id>/",  views.add_review,    name="add_review"),
    path("reviews/edit/<int:review_id>/",  views.edit_review,   name="edit_review"),
    path("reviews/delete/<int:review_id>/", views.delete_review, name="delete_review"),
]