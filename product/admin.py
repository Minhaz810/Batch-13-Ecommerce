from django.contrib import admin
from .models import ProductCategory, Product, ProductVariant, ProductImage

admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)
