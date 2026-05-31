from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class I18NNameMixin(models.Model):
    """UZ/RU/EN nom maydonlari + til bo'yicha tanlash."""

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, blank=True)
    name_en = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name_uz

    def name_for(self, lang: str) -> str:
        return getattr(self, f"name_{lang}", "") or self.name_uz


class Category(I18NNameMixin, TimeStampedModel):
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    icon = models.CharField(max_length=64, blank=True, help_text="Lucide ikon nomi")
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        ordering = ["order", "name_uz"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_uz)
        super().save(*args, **kwargs)


class Brand(I18NNameMixin, TimeStampedModel):
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_uz)
        super().save(*args, **kwargs)


class Product(I18NNameMixin, TimeStampedModel):
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description_uz = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.PROTECT
    )
    brand = models.ForeignKey(
        Brand, related_name="products", null=True, blank=True, on_delete=models.SET_NULL
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=40, unique=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        indexes = [
            models.Index(fields=["is_active", "is_featured"]),
            models.Index(fields=["price"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name_en or self.name_uz)
            self.slug = f"{base}-{self.sku}".lower()
        super().save(*args, **kwargs)

    def description_for(self, lang: str) -> str:
        return getattr(self, f"description_{lang}", "") or self.description_uz

    @property
    def final_price(self):
        return self.discount_price or self.price

    @property
    def discount_percent(self) -> int:
        if self.discount_price and self.price:
            return round((1 - self.discount_price / self.price) * 100)
        return 0

    @property
    def in_stock(self) -> bool:
        return self.stock > 0


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="Tashqi rasm (seed uchun)")
    alt = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta(TimeStampedModel.Meta):
        ordering = ["order"]

    @property
    def src(self) -> str:
        if self.image:
            return self.image.url
        return self.image_url


class Attribute(I18NNameMixin, TimeStampedModel):
    """Masalan: Rang, O'lcham."""

    code = models.SlugField(max_length=40, unique=True)


class AttributeValue(I18NNameMixin, TimeStampedModel):
    attribute = models.ForeignKey(
        Attribute, related_name="values", on_delete=models.CASCADE
    )
    products = models.ManyToManyField(
        Product, related_name="attribute_values", blank=True
    )
