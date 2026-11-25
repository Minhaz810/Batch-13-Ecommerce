from django.db import models
from django.conf import settings
from django.db.models import Q
from Shared.models import TimeStampMixin
from product.models import ProductVariant

class Order(models.Model):

    Status_Choices=[
        ( "pending", "Pending"),
        ( "confirmed", "Confirmed"),
        ( "processing", "Processing"),
        ( "shipped", "Shipped"),
        ( "delivered", "Delivered"),
        ( "cancelled", "Cancelled"),
        ( "refunded", "Refunded")
]
	

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    status = models.CharField(
        max_length=20,
        choices= Status_Choices,
        default='pending'
    )

    shipping_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    customer_note = models.TextField(blank=True)


    class Meta:
        
        constraints = [
            models.CheckConstraint(
                condition=Q(subtotal__gte=0),
                name="order_subtotal_non_negative"
            ),
            models.CheckConstraint(
                condition=Q(shipping_cost__gte=0),
                name="order_shipping_non_negative"
            ),
            models.CheckConstraint(
                condition=Q(discount_amount__gte=0),
                name="order_discount_non_negative"
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name="order_total_non_negative"
            )
        ]

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(TimeStampMixin):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items"
    )
    variant_name = models.CharField(max_length=150)

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField()
    

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="order_item_quantity_positive"
            ),
            models.CheckConstraint(
                condition=Q(unit_price__gte=0),
                name="order_item_price_non_negative"
            )
        ]

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self. variant_name } x {self.quantity}"
