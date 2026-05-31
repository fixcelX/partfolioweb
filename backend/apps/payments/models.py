from django.db import models

from apps.common.models import TimeStampedModel
from apps.orders.models import Order


class Payment(TimeStampedModel):
    class Provider(models.TextChoices):
        CLICK = "click", "Click"
        PAYME = "payme", "Payme"
        STRIPE = "stripe", "Stripe"

    class Status(models.TextChoices):
        CREATED = "created", "Yaratildi"
        PAID = "paid", "To'landi"
        FAILED = "failed", "Xato"

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=Provider.choices)
    transaction_id = models.CharField(max_length=128, blank=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CREATED
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    raw_payload = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.provider}:{self.order.number}:{self.status}"
