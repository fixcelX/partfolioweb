from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.catalog.serializers import ProductListSerializer

from .models import Wishlist


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return wishlist

    def get(self, request):
        wishlist = self._get(request)
        products = wishlist.products.filter(is_active=True).prefetch_related("images")
        return Response(
            ProductListSerializer(products, many=True, context={"request": request}).data
        )


class WishlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product = Product.objects.filter(pk=product_id, is_active=True).first()
        if not product:
            return Response({"detail": "Mahsulot topilmadi.", "errors": {}}, status=404)
        wishlist.products.add(product)
        return Response({"detail": "Sevimlilarga qo'shildi."}, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.remove(product_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
