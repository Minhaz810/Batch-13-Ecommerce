from django.db import models
from django.utils.text import slugify
from Shared.models import TimeStampMixin

class Category(TimeStampMixin):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Brand(TimeStampMixin):
    name = models.CharField(max_length=150, unique=True)
    def __str__(self):
        return self.name

class Product(TimeStampMixin):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ProductImage(TimeStampMixin):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image - {self.product.name}"

class ProductVariant(TimeStampMixin):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    name = models.CharField(
        	max_length=150
            )
    sku = models.CharField(max_length=100)
    
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="variant_price_non_negative"
            ),
        ]
    def __str__(self):
        return f"{self.product.name} - {self.name}"
