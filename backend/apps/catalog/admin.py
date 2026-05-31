from django.contrib import admin

from .models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductImage,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_uz", "slug", "parent", "order")
    list_filter = ("parent",)
    search_fields = ("name_uz", "name_ru", "name_en")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name_uz", "slug")
    search_fields = ("name_uz",)
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name_uz", "category", "brand", "price", "discount_price",
        "stock", "rating", "is_active", "is_featured",
    )
    list_filter = ("is_active", "is_featured", "category", "brand")
    search_fields = ("name_uz", "sku")
    list_editable = ("price", "stock", "is_active", "is_featured")
    inlines = [ProductImageInline]


admin.site.register(Attribute)
admin.site.register(AttributeValue)
