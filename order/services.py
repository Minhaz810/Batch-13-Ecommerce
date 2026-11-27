import logging

from django.contrib.auth.models import User
from django.db import transaction

from cart.models import Cart
from .models import Order, OrderItem

logger = logging.getLogger(__name__)


def _format_address(session, user):
    details = session.customer_details.to_dict() if session.customer_details else {}
    address = details.get('address') or {}
    parts = [
        address.get('line1'),
        address.get('line2'),
        address.get('city'),
        address.get('state'),
        address.get('postal_code'),
        address.get('country'),
    ]
    formatted = ', '.join(p for p in parts if p)
    if not formatted:
        profile = getattr(user, 'customer_profile', None)
        formatted = (profile.address if profile else '') or ''
    return formatted[:200]


def create_order_from_session(session):
    """Turn the paying user's cart into a Paid order, then empty the cart.

    Returns the Order, or None if the session is unpaid, the user is unknown,
    or the cart is already empty (e.g. Stripe retried an event we handled).
    """
    if session.payment_status != 'paid':
        return None

    metadata = session.metadata.to_dict() if session.metadata else {}
    user = User.objects.filter(id=metadata.get('user_id')).first()
    if not user:
        logger.error('Stripe session %s: no matching user', session.id)
        return None

    with transaction.atomic():
        # Lock the cart so a retried event can't build a second order from it.
        cart = (
            Cart.objects.select_for_update()
            .filter(customer__user=user)
            .first()
        )
        if not cart:
            return None

        items = list(cart.items.select_related('variant__product'))
        if not items:
            logger.info('Stripe session %s: cart already empty, skipping', session.id)
            return None

        order = Order.objects.create(
            customer=user,
            address=_format_address(session, user),
            status='Paid',
        )

        for item in items:
            variant = item.variant
            OrderItem.objects.create(
                order=order,
                variant=variant,
                price=variant.product.price,
                quantity=item.quantity,
            )
            if item.quantity > variant.stock:
                logger.warning(
                    'Order %s oversold variant %s (stock %s, ordered %s)',
                    order.id, variant.id, variant.stock, item.quantity,
                )
            variant.stock = max(variant.stock - item.quantity, 0)
            variant.save(update_fields=['stock', 'updated_at'])

        cart.items.all().delete()

    return order
