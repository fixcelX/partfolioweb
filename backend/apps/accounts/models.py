from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel

from .managers import UserManager


class User(AbstractUser):
    """Email bilan login qiluvchi custom foydalanuvchi."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Xaridor"
        SELLER = "seller", "Sotuvchi"
        ADMIN = "admin", "Admin"

    username = None  # email loginga o'tdik
    email = models.EmailField("email", unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email


class Address(TimeStampedModel):
    """Yetkazib berish manzili."""

    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    region = models.CharField("viloyat", max_length=80)
    city = models.CharField("shahar", max_length=80)
    street = models.CharField("ko'cha / uy", max_length=255)
    zip_code = models.CharField(max_length=12, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        verbose_name_plural = "Addresses"

    def __str__(self) -> str:
        return f"{self.city}, {self.street}"

    def save(self, *args, **kwargs):
        # Bitta default manzil bo'lsin
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(
                pk=self.pk
            ).update(is_default=False)
        super().save(*args, **kwargs)
