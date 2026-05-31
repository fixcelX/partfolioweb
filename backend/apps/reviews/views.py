from django.db.models import Avg
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.catalog.models import Product
from apps.orders.models import OrderItem

from .models import Review
from .serializers import ReviewSerializer


class ProductReviewListCreate(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_product(self):
        return generics.get_object_or_404(Product, slug=self.kwargs["slug"])

    def get_queryset(self):
        return Review.objects.filter(product=self.get_product()).select_related("user")

    def perform_create(self, serializer):
        product = self.get_product()
        user = self.request.user
        if Review.objects.filter(product=product, user=user).exists():
            raise ValidationError({"detail": "Siz allaqachon sharh qoldirgansiz."})

        # Faqat sotib olganlar "tasdiqlangan" sharh yozadi
        purchased = OrderItem.objects.filter(
            order__user=user, product=product, order__status__in=["paid", "shipped", "delivered"]
        ).exists()
        if not purchased:
            raise PermissionDenied("Faqat ushbu mahsulotni sotib olganlar sharh yozadi.")

        review = serializer.save(product=product, user=user, is_verified=True)
        self._recalc(product)
        return review

    @staticmethod
    def _recalc(product):
        agg = product.reviews.aggregate(avg=Avg("rating"))
        product.rating = round(agg["avg"] or 0, 2)
        product.reviews_count = product.reviews.count()
        product.save(update_fields=["rating", "reviews_count"])
