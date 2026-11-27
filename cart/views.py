import os

import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from account.models import CustomerProfile
from product.models import ProductVariant
from .models import Cart, CartItem

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


# Create your views here.
@login_required
def add_to_cart(request, variant_id=None):
    if request.method == 'POST':
        variant_id = variant_id or request.POST.get('variant_id')
        if not variant_id:
            messages.error(request, "Please select a product variant.")
            return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

        variant = get_object_or_404(ProductVariant.objects.select_related('product'), id=variant_id)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        # Check stock availability
        if variant.stock <= 0:
            messages.error(request, f"Sorry, '{variant.product.product_name} ({variant.name})' is currently out of stock.")
            return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        cart, _ = Cart.objects.get_or_create(customer=profile)
        cart_item = CartItem.objects.filter(cart=cart, variant=variant).first()

        current_in_cart = cart_item.quantity if cart_item else 0
        new_quantity = current_in_cart + quantity

        if new_quantity > variant.stock:
            available_to_add = variant.stock - current_in_cart
            if available_to_add > 0:
                if cart_item:
                    cart_item.quantity = variant.stock
                    cart_item.save()
                else:
                    CartItem.objects.create(cart=cart, variant=variant, quantity=variant.stock)
                messages.warning(
                    request,
                    f"Only {variant.stock} in stock! Added remaining {available_to_add} item(s) to your cart."
                )
            else:
                messages.warning(
                    request,
                    f"You already have the maximum available stock ({variant.stock}) of '{variant.name}' in your cart."
                )
        else:
            if cart_item:
                cart_item.quantity = new_quantity
                cart_item.save()
            else:
                CartItem.objects.create(cart=cart, variant=variant, quantity=quantity)
            messages.success(
                request,
                f"Added {quantity} x '{variant.product.product_name} ({variant.name})' to your cart!"
            )

        return redirect('cart:cart_detail')

    return redirect('products:product_list')



@login_required
def cart_detail(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    cart, _ = Cart.objects.get_or_create(customer=profile)
    cart_items = cart.items.select_related('variant__product').prefetch_related('variant__images').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': cart.total_items,
        'total_price': cart.total_price,
    }
    return render(request, 'cart_detail.html', context)


def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity <= 0:
            cart_item.delete()
            messages.success(request, f"Removed item from your cart.")
        else:
            if quantity > cart_item.variant.stock:
                cart_item.quantity = cart_item.variant.stock
                cart_item.save()
                messages.warning(
                    request,
                    f"Only {cart_item.variant.stock} available in stock. Adjusted quantity accordingly."
                )
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, "Cart updated successfully.")

    return redirect('cart:cart_detail')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer__user=request.user)
    item_name = f"{cart_item.variant.product.product_name} ({cart_item.variant.name})"
    cart_item.delete()
    messages.success(request, f"Removed '{item_name}' from your cart.")
    return redirect('cart:cart_detail')

@login_required
def create_checkout_session(request):
    if request.method != 'POST':
        return redirect('cart:cart_detail')

    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    cart, _ = Cart.objects.get_or_create(customer=profile)
    items = cart.items.select_related('variant__product')

    if not items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    line_items = []

    for item in items:
        if item.quantity > item.variant.stock:
            messages.error(
                request,
                f'Only {item.variant.stock} of {item.variant} left in stock, '
                f'but your cart has {item.quantity}.',
            )
            return redirect('cart:cart_detail')

        product = item.variant.product

        # Only products synced to Stripe can be checked out — Stripe owns the amount.
        if not product.stripe_price_id:
            messages.error(
                request,
                f'{product.product_name} is not available for checkout yet.',
            )
            return redirect('cart:cart_detail')

        line_items.append({
            'price': product.stripe_price_id,
            'quantity': item.quantity,
        })

    try:
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=line_items,
            customer_email=request.user.email or None,
            # checkout_success checks this to confirm the session belongs to the user.
            metadata={'user_id': str(request.user.id)},
            success_url=request.build_absolute_uri(
                reverse('cart:checkout_success')
            ) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('cart:checkout_cancel')),
        )
    except stripe.StripeError as exc:
        messages.error(request, f'Could not start checkout: {exc.user_message or exc}')
        return redirect('cart:cart_detail')

    return redirect(session.url, permanent=False)


@login_required
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('cart:cart_detail')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        messages.error(request, "Could not verify your payment.")
        return redirect('cart:cart_detail')

    # StripeObject is not a dict in stripe-python v12+, so convert before .get().
    metadata = session.metadata.to_dict() if session.metadata else {}
    if session.payment_status == 'paid' and metadata.get('user_id') == str(request.user.id):
        # The order is created and the cart emptied by the Stripe webhook
        # (order.views.stripe_webhook), not here.
        messages.success(request, "Payment successful! Thank you for your order.")
    else:
        messages.warning(request, "Payment not completed yet.")

    return redirect('cart:cart_detail')


@login_required
def checkout_cancel(request):
    messages.info(request, "Checkout cancelled. Your cart is still saved.")
    return redirect('cart:cart_detail')
