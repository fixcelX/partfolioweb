from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import ProductFilter
from .models import Brand, Category, Product
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        # Daraxt: faqat ildiz kategoriyalar, children nested keladi
        qs = Category.objects.annotate(products_count=Count("products")).order_by(
            "order", "name_uz"
        )
        if self.action == "list":
            return qs.filter(parent__isnull=True).prefetch_related("children")
        return qs


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_class = ProductFilter
    search_fields = [
        "name_uz", "name_ru", "name_en", "sku",
        "brand__name_uz", "brand__name_ru", "brand__name_en",
        "category__name_uz", "category__name_ru", "category__name_en",
        "description_uz", "description_ru", "description_en",
    ]
    ordering_fields = ["price", "rating", "sold_count", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related("category", "brand")
            .prefetch_related("images")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=False)
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)[:12]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False)
    def new(self, request):
        qs = self.get_queryset().order_by("-created_at")[:12]
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False)
    def bestsellers(self, request):
        qs = self.get_queryset().order_by("-sold_count")[:12]
        return Response(self.get_serializer(qs, many=True).data)
