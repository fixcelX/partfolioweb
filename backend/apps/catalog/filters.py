import django_filters as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(method="filter_category")
    brand = filters.CharFilter(field_name="brand__slug")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    rating = filters.NumberFilter(field_name="rating", lookup_expr="gte")
    in_stock = filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "brand", "min_price", "max_price", "rating", "in_stock"]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_category(self, queryset, name, value):
        """Slug bo'yicha kategoriya — bola turkumlarni ham qamrab oladi."""
        from django.db.models import Q

        return queryset.filter(
            Q(category__slug=value) | Q(category__parent__slug=value)
        )
