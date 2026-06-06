"""Root URL konfiguratsiyasi.

- `/`                — server-rendered premium web (storefront, HTML/CSS/JS)
- `/api/v1/`         — REST API (mobil ilova / integratsiyalar uchun saqlanadi)
- `/admin/`          — Django admin
- `/api/docs/`       — Swagger / OpenAPI
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import set_language
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_v1 = [
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.catalog.urls")),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("payments/", include("apps.payments.urls")),
    path("", include("apps.reviews.urls")),
    path("wishlist/", include("apps.wishlist.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1)),
    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Til almashtirish (UZ / RU / EN) — sessiya + cookie
    path("i18n/setlang/", set_language, name="set_language"),
    # Server-rendered web frontend (eng oxirida — boshqa prefikslarni ushlamasin)
    path("", include("apps.storefront.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Maxsus xato sahifalari (DEBUG=False da)
handler404 = "apps.storefront.views.handler404"
handler500 = "apps.storefront.views.handler500"
