from django.conf import settings
from django.db import models

from apps.catalog.models import Product
from apps.common.models import TimeStampedModel


class Wishlist(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="wishlist", on_delete=models.CASCADE
    )
    products = models.ManyToManyField(Product, related_name="wishlisted_by", blank=True)
