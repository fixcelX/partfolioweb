from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order

from .providers import PaymentError, get_provider


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, provider):
        number = request.data.get("order")
        order = Order.objects.filter(number=number, user=request.user).first()
        if not order:
            return Response(
                {"detail": "Buyurtma topilmadi.", "errors": {}},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            data = get_provider(provider).create(order)
        except PaymentError as exc:
            return Response({"detail": str(exc), "errors": {}}, status=400)
        return Response(data, status=status.HTTP_201_CREATED)


class PaymentWebhookView(APIView):
    """Provayder callback — auth yo'q, imzo bilan himoyalangan."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, provider):
        try:
            result = get_provider(provider).handle_webhook(request.data)
        except PaymentError as exc:
            return Response({"detail": str(exc), "errors": {}}, status=400)
        return Response(result)
