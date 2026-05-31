from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CartItemSerializer, CartSerializer
from .services import get_or_create_cart


class CartView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart, context={"request": request}).data)


class CartItemViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart = get_or_create_cart(self.request)
        return cart.items.select_related("product").prefetch_related("product__images")

    def create(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)

        item = cart.items.filter(product=product).first()
        if item:
            item.quantity = min(item.quantity + quantity, product.stock)
            item.save()
        else:
            item = serializer.save(cart=cart)
        out = CartSerializer(cart, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.delete()

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart, context={"request": request}).data)
