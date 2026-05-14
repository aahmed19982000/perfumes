from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.index, name='index'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/create/', views.coupon_upsert, name='coupon_create'),
    path('coupons/edit/<int:pk>/', views.coupon_upsert, name='coupon_edit'),
    path('header-settings/', views.header_settings, name='header_settings'),
    path('footer-settings/', views.footer_settings, name='footer_settings'),
    
    path('wishlists/', views.wishlist_list, name='wishlist_list'),
    path('wishlists/<int:pk>/', views.wishlist_detail, name='wishlist_detail'),

    path('login/', views.DashboardLoginView.as_view(), name='login'),
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_upsert, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_upsert, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),

    path('subcategories/', views.subcategory_list, name='subcategory_list'),
    path('subcategories/create/', views.subcategory_upsert, name='subcategory_create'),
    path('subcategories/edit/<int:pk>/', views.subcategory_upsert, name='subcategory_edit'),

    path('brands/', views.brand_list, name='brand_list'),
    path('brands/create/', views.brand_upsert, name='brand_create'),
    path('brands/edit/<int:pk>/', views.brand_upsert, name='brand_edit'),
    
    path('banners/', views.banner_list, name='banner_list'),
    path('banners/create/', views.banner_upsert, name='banner_create'),
    path('banners/edit/<int:pk>/', views.banner_upsert, name='banner_edit'),
    
    path('governorates/', views.governorate_list, name='governorate_list'),
    path('governorates/create/', views.governorate_upsert, name='governorate_create'),
    path('governorates/edit/<int:pk>/', views.governorate_upsert, name='governorate_edit'),

    path('cities/', views.city_list, name='city_list'),
    path('cities/create/', views.city_upsert, name='city_create'),
    path('cities/edit/<int:pk>/', views.city_upsert, name='city_edit'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/edit/<int:pk>/', views.customer_edit, name='customer_edit'),
    
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/edit/<int:pk>/', views.edit_staff, name='edit_staff'),


    path('offers/',                  views.offer_list,   name='offer_list'),
    path('offers/create/',           views.offer_upsert, name='offer_create'),
    path('offers/edit/<int:pk>/',    views.offer_upsert, name='offer_edit'),
    path('offers/delete/<int:pk>/',  views.offer_delete, name='offer_delete'),
]
