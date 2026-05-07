from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("password-change/", views.change_password_view, name="password_change"),
    path("addresses/", views.address_list_view, name="address_list"),
    path("addresses/add/", views.address_create_view, name="address_create"),
    path("addresses/edit/<int:pk>/", views.address_edit_view, name="address_edit"),
    path("addresses/delete/<int:pk>/", views.address_delete_view, name="address_delete"),
    path("api/cities/", views.get_cities, name="get_cities"),
]