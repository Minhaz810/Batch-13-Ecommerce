from django.db import models
from django.db.models import Q
import uuid
from Shared.models import TimeStampMixin

class Payment(TimeStampMixin):

    class Method(models.TextChoices):
        CASH_ON_DELIVERY = "cod", "Cash on Delivery"
        CARD = "card", "Card"
        MOBILE_BANKING = "mobile_banking", "Mobile Banking"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(
        "order.Order",
        on_delete=models.PROTECT,
        related_name="payments"
    )

    payment_method = models.CharField(
        max_length=30,
        choices=Method.choices
    )

    transaction_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    gateway_transaction_id = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    paid_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="payment_amount_positive"
            )
        ]

    def __str__(self):
        return f"Payment - {self.transaction_id}"
