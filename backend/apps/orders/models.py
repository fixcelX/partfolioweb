from django.conf import settings
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PAID = "paid", "To'langan"
        SHIPPED = "shipped", "Jo'natildi"
        DELIVERED = "delivered", "Yetkazildi"
        CANCELLED = "cancelled", "Bekor qilindi"

    class PaymentMethod(models.TextChoices):
        CLICK = "click", "Click"
        PAYME = "payme", "Payme"
        STRIPE = "stripe", "Stripe"
        COD = "cod", "Yetkazganda naqd"

    number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)

    # Manzil snapshot
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    region = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    street = models.CharField(max_length=255)

    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            super().save(*args, **kwargs)
            self.number = f"UZM-{self.pk:06d}"
            return super().save(update_fields=["number"])
        return super().save(*args, **kwargs)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, null=True, on_delete=models.SET_NULL
    )
    # Snapshot — mahsulot o'chsa ham buyurtma saqlanadi
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.price * self.quantity
