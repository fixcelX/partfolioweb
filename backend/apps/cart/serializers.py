from rest_framework import serializers

from apps.catalog.models import Product
from apps.catalog.serializers import ProductListSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
    )
    subtotal = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_id", "quantity", "subtotal")

    def validate(self, attrs):
        product = attrs.get("product") or self.instance.product
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", 1))
        if quantity > product.stock:
            raise serializers.ValidationError(
                {"quantity": f"Omborda faqat {product.stock} dona mavjud."}
            )
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "items", "total", "total_quantity")
