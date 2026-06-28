# products/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator
from .models import Product, Category, Brand, SubCategory


def product_list(request):
    products = Product.objects.filter(is_active=True)

    # ── 1. Full-Text Search ──────────────────────────────────────
    search = request.GET.get("search")
    if search:
        vector = SearchVector("name_ar", weight="A") + \
                 SearchVector("name_en", weight="A") + \
                 SearchVector("description_ar", weight="B") + \
                 SearchVector("description_en", weight="B") + \
                 SearchVector("sku", weight="A")
        
        query = SearchQuery(search)
        products = products.annotate(
            rank=SearchRank(vector, query)
        ).filter(rank__gte=0.1).order_by("-rank")
    else:
        # ترتيب افتراضي لو مفيش بحث
        products = products.order_by("-created_at")

    # ── 2. Multi-Filtering (IDs list) ───────────────────────────
    category_ids     = request.GET.getlist("category")
    brand_ids        = request.GET.getlist("brand")
    sub_category_ids = request.GET.getlist("sub_category")

    if category_ids:
        products = products.filter(category_id__in=category_ids)
    if brand_ids:
        products = products.filter(brand_id__in=brand_ids)
    if sub_category_ids:
        products = products.filter(sub_category_id__in=sub_category_ids)

    # ── 3. Price Range ──────────────────────────────────────────
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # ── 4. Special Filters (latest, featured) ────────────────────
    data_from = request.GET.get("data_from")
    if data_from == "latest":
        products = products.order_by("-created_at")
    elif data_from == "featured":
        products = products.filter(is_featured=True)

    # ── 5. Sorting ──────────────────────────────────────────────
    sort_by = request.GET.get("sort")
    if sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
    elif sort_by == "oldest":
        products = products.order_by("created_at")

    # ── Pagination ──────────────────────────────────────────────
    paginator   = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj    = paginator.get_page(page_number)

    # بيانات الفلاتر (للـ UI)
    all_categories = Category.objects.filter(is_active=True).prefetch_related('sub_categories')
    all_brands     = Brand.objects.filter(is_active=True)
    
    # حساب نطاق الأسعار للمنزلق (Slider)
    price_stats = Product.objects.filter(is_active=True).aggregate(Min('price'), Max('price'))

    return render(request, "products/product_list.html", {
        "products":       page_obj,
        "categories":     all_categories,
        "brands":         all_brands,
        "price_stats":    price_stats,
        "selected_cats":  [int(i) for i in category_ids if i.isdigit()],
        "selected_sub_cats": [int(i) for i in sub_category_ids if i.isdigit()],
        "selected_brands":[int(i) for i in brand_ids if i.isdigit()],
        "min_p":          min_price,
        "max_p":          max_price,
        "current_search": search,
        "current_sort":   sort_by,
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