"""Storefront template yordamchilari: narx formati, lokalizatsiya, SVG ikon,
yulduzli reyting va querystring qurish.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

register = template.Library()


# ---------------------------------------------------------------------------
# Narx: 2640000.00 -> "2 640 000"
# ---------------------------------------------------------------------------
@register.filter
def som(value):
    try:
        n = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value
    return f"{int(n):,}".replace(",", " ")  # bo'sh joy = non-breaking space


# ---------------------------------------------------------------------------
# Lokalizatsiya: model obyektidan name/description ni joriy tilda olish
#   {{ product|loc }}            -> name (joriy til)
#   {{ product|loc:"description" }}
# ---------------------------------------------------------------------------
@register.filter
def loc(obj, field: str = "name"):
    lang = (get_language() or "uz")[:2]
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    if obj is None:
        return ""
    val = getattr(obj, f"{field}_{lang}", "") or getattr(obj, f"{field}_uz", "")
    return val


# ---------------------------------------------------------------------------
# {count}/{number} kabi placeholderni qiymat bilan almashtirish
#   {{ t.product.onlyLeft|fmt:product.stock }}
# ---------------------------------------------------------------------------
@register.filter
def fmt(value, arg):
    if not isinstance(value, str):
        return value
    return re.sub(r"\{[^}]+\}", str(arg), value, count=1)


@register.filter
def mul(a, b):
    try:
        return Decimal(str(a)) * Decimal(str(b))
    except (InvalidOperation, TypeError, ValueError):
        return ""


@register.filter
def get(d, key):
    """dict yoki obyektdan kalit bo'yicha olish (xavfsiz)."""
    if d is None:
        return None
    if hasattr(d, "get"):
        return d.get(key)
    return getattr(d, str(key), None)


# ---------------------------------------------------------------------------
# Yulduzli reyting — kasrli (masalan 4.6) ni ham aniq ko'rsatadi
# ---------------------------------------------------------------------------
@register.simple_tag
def stars(value, size: str = ""):
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    v = max(0.0, min(5.0, v))
    pct = v / 5 * 100
    cls = "stars" + (f" stars--{size}" if size else "")
    return format_html(
        '<span class="{}" role="img" aria-label="{} / 5">'
        '<span class="stars__bg">★★★★★</span>'
        '<span class="stars__fill" style="width:{}%">★★★★★</span>'
        "</span>",
        cls,
        f"{v:.1f}",
        f"{pct:.2f}",
    )


# ---------------------------------------------------------------------------
# Inline SVG ikonlar (lucide uslubida). {% icon "cart" cls="..." %}
# ---------------------------------------------------------------------------
ICONS: dict[str, str] = {
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "grid": '<rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20M2 12h20"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "chevron-up": '<path d="m18 15-6-6-6 6"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "truck": '<path d="M14 18V6a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h1"/><path d="M14 9h4l3 3v5a1 1 0 0 1-1 1h-1"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/><path d="M8 18h6"/>',
    "shield-check": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "tag": '<path d="M12.59 2.59A2 2 0 0 0 11.17 2H4a2 2 0 0 0-2 2v7.17a2 2 0 0 0 .59 1.41l8.7 8.7a2.43 2.43 0 0 0 3.42 0l6.58-6.58a2.43 2.43 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r="1.2" fill="currentColor"/>',
    "arrow-right": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "arrow-up": '<path d="m5 12 7-7 7 7M12 19V5"/>',
    "minus": '<path d="M5 12h14"/>',
    "plus": '<path d="M5 12h14M12 5v14"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "sliders": '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/><line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="3" y1="20" y2="20"/><line x1="14" x2="14" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "trash": '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>',
    "menu": '<path d="M4 12h16M4 6h16M4 18h16"/>',
    "package": '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>',
    "map-pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92Z"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "send": '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4Z"/>',
    "instagram": '<rect width="20" height="20" x="2" y="2" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "percent": '<line x1="19" x2="5" y1="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "credit-card": '<rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/>',
    "rotate": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
    "headphones": '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5a9 9 0 0 1 18 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/>',
    "badge-check": '<path d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path d="m9 12 2 2 4-4"/>',
    "store": '<path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"/><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"/><path d="M2 7h20"/>',
    "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C11 3 12 8 12 8s1-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    # Kategoriya ikonlari
    "smartphone": '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "washing-machine": '<path d="M3 6h3M17 6h.01"/><rect width="18" height="20" x="3" y="2" rx="2"/><circle cx="12" cy="13" r="5"/><path d="M12 18a2.5 2.5 0 0 0 0-5 2.5 2.5 0 0 1 0-5"/>',
    "shirt": '<path d="M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "sparkles": '<path d="m12 3-1.9 5.8L4 10l6.1 1.2L12 17l1.9-5.8L20 10l-6.1-1.2z"/><path d="M19 3v3M20.5 4.5h-3"/>',
    "dumbbell": '<path d="M6 7v10M18 7v10M3.5 9.5v5M20.5 9.5v5M6 12h12"/>',
    "baby": '<path d="M9 12h.01M15 12h.01M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><path d="M2.13 13.4a2 2 0 0 1 0-2.8A9 9 0 0 1 12 3a9 9 0 0 1 9.87 7.6 2 2 0 0 1 0 2.8A9 9 0 0 1 12 21a9 9 0 0 1-9.87-7.6Z"/>',
    "car": '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>',
}


@register.simple_tag
def order_steps(status):
    """Buyurtma holati timeline'i uchun 4 bosqich (joriy tilda).
    'cancelled' bo'lsa bo'sh ro'yxat qaytadi (timeline ko'rsatilmaydi)."""
    from apps.storefront.translations import get_translations

    seq = ["pending", "paid", "shipped", "delivered"]
    if status not in seq:
        return []
    lang = (get_language() or "uz")[:2]
    labels = get_translations(lang)["status"]
    idx = seq.index(status)
    return [
        {"label": labels.get(key, key), "num": i + 1, "done": i < idx, "active": i == idx}
        for i, key in enumerate(seq)
    ]


@register.simple_tag
def icon(name, cls: str = "", size: int = 0, fill: str = "none", sw: float = 2):
    inner = ICONS.get(name)
    if inner is None:
        inner = '<circle cx="12" cy="12" r="9"/>'
    dim = f' width="{size}" height="{size}"' if size else ""
    return mark_safe(
        f'<svg class="icon {cls}" viewBox="0 0 24 24" fill="{fill}" '
        f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true"{dim}>{inner}</svg>'
    )


# ---------------------------------------------------------------------------
# Joriy querystring'ni saqlab, ayrim parametrlarni o'zgartirish
#   <a href="?{% qs request page=2 %}">  yoki  ?{% qs request ordering='price' page=None %}
# (None bersa — parametr olib tashlanadi)
# ---------------------------------------------------------------------------
@register.simple_tag
def qs(request, **kwargs):
    params = request.GET.copy()
    for key, val in kwargs.items():
        if val is None or val == "":
            params.pop(key, None)
        else:
            params[key] = val
    return params.urlencode()
