from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "status", "payment_method", "total", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("number", "user__email", "phone")
    list_editable = ("status",)
    inlines = [OrderItemInline]
    readonly_fields = ("number", "total")
