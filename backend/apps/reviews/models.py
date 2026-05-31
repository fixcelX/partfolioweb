from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel


class Review(TimeStampedModel):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False, help_text="Sotib olgan foydalanuvchi")

    class Meta(TimeStampedModel.Meta):
        unique_together = ("product", "user")

    def __str__(self) -> str:
        return f"{self.product.name_uz} — {self.rating}★"
