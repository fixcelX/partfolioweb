from django.urls import path

from .views import CreatePaymentView, PaymentWebhookView

urlpatterns = [
    path("<str:provider>/create/", CreatePaymentView.as_view(), name="payment-create"),
    path("<str:provider>/webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
]
