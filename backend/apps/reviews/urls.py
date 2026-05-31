from django.urls import path

from .views import ProductReviewListCreate

urlpatterns = [
    path(
        "products/<slug:slug>/reviews/",
        ProductReviewListCreate.as_view(),
        name="product-reviews",
    ),
]
