from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
