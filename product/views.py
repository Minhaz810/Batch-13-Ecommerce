from django.shortcuts import render,get_object_or_404
from product.models import Product,ProductVariant,ProductCategory
from django.db.models import Q

# Create your views here.
def product_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    products = Product.objects.select_related('product_category').prefetch_related('variants__images', 'reviews').all()

    # Search filter by product name or category name
    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(product_category__category_name__icontains=query) |
            Q(description__icontains=query)
        )

    # Category filter
    selected_category = None
    if category_slug:
        selected_category = ProductCategory.objects.filter(slug=category_slug).first()
        if selected_category:
            products = products.filter(product_category=selected_category)

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-created_at')

    categories = ProductCategory.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'sort_by': sort_by,
        'total_count': products.count(),
    }
    return render(request, 'product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('product_category'),
        slug = slug,
    )

    return render(request, 'product_detail.html', {
        'product': product,
        'variants': product.variants.all(),
    })