import logging
import os

import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import create_order_from_session

logger = logging.getLogger(__name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    if not webhook_secret:
        logger.error('STRIPE_WEBHOOK_SECRET is not set')
        return HttpResponse(status=500)

    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get('Stripe-Signature', ''),
            webhook_secret,
        )
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    # checkout.session.completed fires for card payments; delayed methods
    # (bank debits etc.) arrive later as async_payment_succeeded.
    if event.type in ('checkout.session.completed', 'checkout.session.async_payment_succeeded'):
        print("even asche!!!")
        print(event.type)
        print(event.data.object)
        create_order_from_session(event.data.object)

    return HttpResponse(status=200)
