from django.db import transaction
from rest_framework import serializers

from apps.cart.services import get_or_create_cart

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    product_slug = serializers.SlugField(source="product.slug", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_slug", "product_name", "price", "quantity", "subtotal")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "number", "status", "status_display", "payment_method",
            "full_name", "phone", "region", "city", "street",
            "total", "items", "created_at",
        )
        read_only_fields = ("number", "status", "total")


class CheckoutSerializer(serializers.Serializer):
    """Savatdan buyurtma yaratadi (atomik, stock kamayadi)."""

    full_name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=20)
    region = serializers.CharField(max_length=80)
    city = serializers.CharField(max_length=80)
    street = serializers.CharField(max_length=255)
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)

    def create(self, validated_data):
        request = self.context["request"]
        cart = get_or_create_cart(request)
        items = list(cart.items.select_related("product"))
        if not items:
            raise serializers.ValidationError({"detail": "Savat bo'sh."})

        with transaction.atomic():
            order = Order.objects.create(user=request.user, **validated_data)
            total = 0
            for item in items:
                product = item.product
                # Stockni qulflab tekshirish
                locked = product.__class__.objects.select_for_update().get(pk=product.pk)
                if item.quantity > locked.stock:
                    raise serializers.ValidationError(
                        {"detail": f"'{locked.name_uz}' uchun omborda yetarli emas."}
                    )
                locked.stock -= item.quantity
                locked.sold_count += item.quantity
                locked.save(update_fields=["stock", "sold_count"])

                price = locked.final_price
                OrderItem.objects.create(
                    order=order,
                    product=locked,
                    product_name=locked.name_uz,
                    price=price,
                    quantity=item.quantity,
                )
                total += price * item.quantity

            order.total = total
            order.save(update_fields=["total"])
            cart.items.all().delete()
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data
