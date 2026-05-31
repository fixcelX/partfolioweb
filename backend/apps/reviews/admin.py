from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_verified", "created_at")
    list_filter = ("rating", "is_verified")
    search_fields = ("product__name_uz", "user__email")
