from django.db import models
from shared.models import TimestampMixin

# Create your models here.
class ProductCategory(TimestampMixin):
    category_name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)

    class Meta:
        # Will explain later
        verbose_name_plural = 'product categories'

    def __str__(self):
        return self.category_name


class Product(TimestampMixin):
    product_name = models.CharField(max_length=200)
    product_category = models.ForeignKey(
        ProductCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
    )
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_product_id = models.CharField(max_length=200,null=True,blank=True)
    stripe_price_id = models.CharField(max_length=200,null=True,blank=True)


    def __str__(self):
        return self.product_name

class ProductVariant(TimestampMixin):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
    )
    name = models.CharField(max_length=150)
    color = models.CharField(max_length=50, blank=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.product.product_name} - {self.name}'

class ProductImage(TimestampMixin):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='product_variant_images/')

    def __str__(self):
        return f'Image for {self.variant.product.product_name}-{self.variant.name}'