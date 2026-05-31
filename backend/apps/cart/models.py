from django.conf import settings
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel


class Cart(TimeStampedModel):
    """Auth foydalanuvchi yoki anonim sessiya saviti."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="cart",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    session_key = models.CharField(max_length=64, blank=True, db_index=True)

    @property
    def total(self):
        return sum((i.subtotal for i in self.items.all()), start=0)

    @property
    def total_quantity(self) -> int:
        return sum(i.quantity for i in self.items.all())


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta(TimeStampedModel.Meta):
        unique_together = ("cart", "product")
        ordering = ["created_at"]

    @property
    def subtotal(self):
        return self.product.final_price * self.quantity
