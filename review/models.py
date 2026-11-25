from django.db import models
from django.conf import settings
from django.db.models import Q
from Shared.models import TimeStampMixin
from product.models import Product

class Review(TimeStampMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="review_rating_between_1_and_5"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating})"
