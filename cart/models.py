from django.db import models
from shared.models import TimestampMixin
from account.models import CustomerProfile
from product.models import ProductVariant

# Create your models here.
class Cart(TimestampMixin):
    customer = models.OneToOneField(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='cart',
    )

    def __str__(self):
        return f'Cart of {self.customer}'


class CartItem(TimestampMixin):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'variant')

    def __str__(self):
        return f'Cart Item-{self.variant.product.product_name}-{self.variant.name}'