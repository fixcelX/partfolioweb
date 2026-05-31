from rest_framework import serializers

from .models import Brand, Category, Product, ProductImage


def get_lang(context) -> str:
    """?lang= yoki Accept-Language dan tilni aniqlaydi (default uz)."""
    request = context.get("request")
    if request is None:
        return "uz"
    lang = request.query_params.get("lang")
    if not lang:
        accept = request.headers.get("Accept-Language", "uz")
        lang = accept.split(",")[0].split("-")[0].strip()
    return lang if lang in ("uz", "ru", "en") else "uz"


class LocalizedNameMixin(serializers.Serializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj) -> str:
        return obj.name_for(get_lang(self.context))


class BrandSerializer(LocalizedNameMixin, serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "logo")


class CategorySerializer(LocalizedNameMixin, serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    products_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "icon", "image", "order", "children", "products_count")

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True, context=self.context).data


class ProductImageSerializer(serializers.ModelSerializer):
    src = serializers.CharField(read_only=True)

    class Meta:
        model = ProductImage
        fields = ("id", "src", "alt", "order")


class ProductListSerializer(LocalizedNameMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "price", "discount_price", "final_price",
            "discount_percent", "rating", "reviews_count", "sold_count",
            "stock", "in_stock", "is_featured", "image",
        )

    def get_image(self, obj):
        first = obj.images.all().first()
        return first.src if first else None


class ProductDetailSerializer(ProductListSerializer):
    description = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    similar = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "description", "images", "category", "brand", "sku", "similar",
        )

    def get_description(self, obj) -> str:
        return obj.description_for(get_lang(self.context))

    def get_similar(self, obj):
        qs = (
            Product.objects.filter(category=obj.category, is_active=True)
            .exclude(pk=obj.pk)
            .prefetch_related("images")[:8]
        )
        return ProductListSerializer(qs, many=True, context=self.context).data
