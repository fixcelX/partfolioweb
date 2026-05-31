from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import CheckoutSerializer, OrderSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    lookup_field = "number"

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items", "items__product")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CheckoutSerializer
        return OrderSerializer
