from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import CustomerProfile
from shared.models import TimestampMixin
from product.models import Product


class Review(TimestampMixin):
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.customer.username} - {self.product.product_name} ({self.rating}/5)"