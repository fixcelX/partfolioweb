"""Har bir sahifa render'iga qo'shiladigan global kontekst.

- `t`              : joriy til tarjimalari (dict)
- `current_lang`  : 'uz' | 'ru' | 'en'
- `cart_count`    : savatdagi mahsulotlar soni (badge uchun)
- `nav_categories`: header mega-menyu uchun ildiz turkumlar (+ children)
- `wishlist_ids`  : foydalanuvchi sevimlilaridagi mahsulot id'lari (yurakcha holati)
"""
from __future__ import annotations

from django.db.models import Sum
from django.utils.translation import get_language

from .translations import get_translations

_SKIP_PREFIXES = ("/admin", "/api", "/i18n", "/static", "/media")


def storefront(request):
    path = request.path or "/"
    if path.startswith(_SKIP_PREFIXES):
        # Admin / API render'larida ortiqcha so'rov bajarmaymiz
        return {}

    lang = (get_language() or "uz")[:2]
    if lang not in ("uz", "ru", "en"):
        lang = "uz"

    return {
        "t": get_translations(lang),
        "current_lang": lang,
        "cart_count": _cart_count(request),
        "nav_categories": _nav_categories(),
        "wishlist_ids": _wishlist_ids(request),
    }


def _cart_count(request) -> int:
    from apps.cart.models import Cart

    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            key = request.session.session_key
            cart = Cart.objects.filter(session_key=key, user__isnull=True).first() if key else None
        if not cart:
            return 0
        agg = cart.items.aggregate(n=Sum("quantity"))
        return int(agg["n"] or 0)
    except Exception:
        return 0


def _nav_categories():
    from apps.catalog.models import Category

    try:
        return list(
            Category.objects.filter(parent__isnull=True)
            .prefetch_related("children")
            .order_by("order", "name_uz")
        )
    except Exception:
        return []


def _wishlist_ids(request) -> set[int]:
    if not request.user.is_authenticated:
        return set()
    try:
        from apps.wishlist.models import Wishlist

        wl = Wishlist.objects.filter(user=request.user).first()
        if not wl:
            return set()
        return set(wl.products.values_list("id", flat=True))
    except Exception:
        return set()
