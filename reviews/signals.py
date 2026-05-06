# apps/reviews/signals.py
# بيحدّث ReviewSummary تلقائياً كل ما اتضاف أو اتحذف تقييم

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review, ReviewSummary


def _refresh_summary(product):
    approved = Review.objects.filter(product=product, is_approved=True)
    agg      = approved.aggregate(avg=Avg("rating"), total=Count("id"))

    summary, _ = ReviewSummary.objects.get_or_create(product=product)
    summary.avg_rating    = round(agg["avg"] or 0, 1)
    summary.total_reviews = agg["total"] or 0

    for star in range(1, 6):
        setattr(summary, f"count_{star}_star",
                approved.filter(rating=star).count())

    summary.save()


@receiver(post_save,   sender=Review)
def on_review_save(sender, instance, **kwargs):
    _refresh_summary(instance.product)


@receiver(post_delete, sender=Review)
def on_review_delete(sender, instance, **kwargs):
    _refresh_summary(instance.product)