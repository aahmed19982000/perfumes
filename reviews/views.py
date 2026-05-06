# apps/reviews/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from products.models import Product


# ── إضافة تقييم جديد ─────────────────────────────────────────────
@require_POST
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # تحقق إن العميل اشترى المنتج فعلاً (اختياري)
    # has_purchased = request.user.orders.filter(items__product=product).exists()

    # منع التقييم المكرر
    if Review.objects.filter(product=product, customer=request.user).exists():
        messages.warning(request, "لقد قمت بتقييم هذا المنتج مسبقاً")
        return redirect("product_detail", slug=product.slug)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review          = form.save(commit=False)
        review.product  = product
        review.customer = request.user
        review.save()
        messages.success(request, "شكراً! تم إضافة تقييمك بنجاح")
    else:
        messages.error(request, "يرجى التحقق من البيانات المدخلة")

    return redirect("product_detail", slug=product.slug)


# ── تعديل تقييم موجود ────────────────────────────────────────────
@require_POST
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, customer=request.user)

    if not review.can_edit:
        messages.error(request, "انتهت مدة تعديل هذا التقييم (48 ساعة)")
        return redirect("product_detail", slug=review.product.slug)

    form = ReviewForm(request.POST, instance=review)
    if form.is_valid():
        form.save()
        messages.success(request, "تم تحديث تقييمك بنجاح")

    return redirect("product_detail", slug=review.product.slug)


# ── حذف تقييم ────────────────────────────────────────────────────
@require_POST
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, customer=request.user)
    slug   = review.product.slug
    review.delete()
    messages.success(request, "تم حذف تقييمك")
    return redirect("product_detail", slug=slug)