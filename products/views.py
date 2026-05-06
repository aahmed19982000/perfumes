# products/views.py

from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Brand, SubCategory


def product_list(request):
    products = Product.objects.filter(is_active=True)

    # ── فلترة ─────────────────────────────────────────────────────
    category_id     = request.GET.get("category_id")
    sub_category_id = request.GET.get("sub_category_id")
    brand_id        = request.GET.get("brand_id")
    search          = request.GET.get("search")
    data_from       = request.GET.get("data_from")

    if category_id:
        products = products.filter(category_id=category_id)
    if sub_category_id:
        products = products.filter(sub_category_id=sub_category_id)
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if search:
        products = products.filter(name_ar__icontains=search) | \
                   products.filter(name_en__icontains=search)
    if data_from == "latest":
        products = products.order_by("-created_at")
    elif data_from == "featured":
        products = products.filter(is_featured=True)

    return render(request, "products/product_list.html", {
        "products":   products,
        "categories": Category.objects.filter(is_active=True),
        "brands":     Brand.objects.filter(is_active=True),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
    ).exclude(pk=product.pk)[:12]

    is_in_wishlist = False
    if request.user.is_authenticated:
        try:
            is_in_wishlist = request.user.wishlist.items.filter(
                product=product
            ).exists()
        except Exception:
            pass

    user_reviewed = False
    if request.user.is_authenticated:
        user_reviewed = product.reviews.filter(
            customer=request.user
        ).exists()

    return render(request, "products/product_detail.html", {
        "product":          product,
        "related_products": related_products,
        "is_in_wishlist":   is_in_wishlist,
        "user_reviewed":    user_reviewed,
    })