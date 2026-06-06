"""Storefront — server-rendered premium web frontend.

Sahifalar modeldan to'g'ridan-to'g'ri render qilinadi (SEO + JS'siz ham ishlaydi),
dinamik amallar (savatga qo'shish, sevimlilar, qidiruv) vanilla JS + bu yerdagi
JSON endpointlar orqali bajariladi. Mavjud DRF API /api/v1/ da o'zgarishsiz qoladi.
"""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import get_language
from django.views.decorators.http import require_POST

from apps.accounts.models import Address
from apps.cart.services import get_or_create_cart
from apps.catalog.models import Brand, Category, Product
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import CheckoutSerializer
from apps.reviews.models import Review
from apps.wishlist.models import Wishlist

from .forms import AddressForm, LoginForm, ProfileForm, RegisterForm
from .translations import get_translations

User = get_user_model()

PAGE_SIZE = 24
ORDERINGS = {"-created_at", "price", "-price", "-rating", "-sold_count"}


def _lang() -> str:
    lang = (get_language() or "uz")[:2]
    return lang if lang in ("uz", "ru", "en") else "uz"


def _t() -> dict:
    return get_translations(_lang())


# ===========================================================================
# Sahifalar
# ===========================================================================
def home(request):
    base = (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")
        .prefetch_related("images")
    )
    ctx = {
        "featured": list(base.filter(is_featured=True)[:12]),
        "bestsellers": list(base.order_by("-sold_count")[:12]),
        "new_products": list(base.order_by("-created_at")[:12]),
        "categories": list(
            Category.objects.filter(parent__isnull=True).order_by("order", "name_uz")
        ),
    }
    return render(request, "storefront/home.html", ctx)


def _filter_products(request, category_slug=None, query=None):
    qs = (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")
        .prefetch_related("images")
    )
    g = request.GET

    cat = category_slug or g.get("category")
    if cat:
        qs = qs.filter(Q(category__slug=cat) | Q(category__parent__slug=cat))

    if brand := g.get("brand"):
        qs = qs.filter(brand__slug=brand)

    if (mn := g.get("min_price")) and mn.isdigit():
        qs = qs.filter(price__gte=mn)
    if (mx := g.get("max_price")) and mx.isdigit():
        qs = qs.filter(price__lte=mx)

    if rating := g.get("rating"):
        try:
            qs = qs.filter(rating__gte=float(rating))
        except ValueError:
            pass

    if g.get("in_stock") in ("true", "1", "on"):
        qs = qs.filter(stock__gt=0)

    q = query if query is not None else g.get("q")
    if q:
        qs = qs.filter(
            Q(name_uz__icontains=q)
            | Q(name_ru__icontains=q)
            | Q(name_en__icontains=q)
            | Q(sku__icontains=q)
            | Q(brand__name_uz__icontains=q)
            | Q(brand__name_en__icontains=q)
            | Q(category__name_uz__icontains=q)
            | Q(description_uz__icontains=q)
        ).distinct()

    ordering = g.get("ordering", "-created_at")
    if ordering not in ORDERINGS:
        ordering = "-created_at"
    return qs.order_by(ordering)


def _paginate(qs, page):
    from django.core.paginator import Paginator

    paginator = Paginator(qs, PAGE_SIZE)
    try:
        page = int(page or 1)
    except (TypeError, ValueError):
        page = 1
    return paginator.get_page(page)


def catalog(request, category_slug=None, title=None, query=None):
    qs = _filter_products(request, category_slug=category_slug, query=query)
    page_obj = _paginate(qs, request.GET.get("page"))

    active_category = None
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()

    ctx = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "total_count": page_obj.paginator.count,
        "brands": list(Brand.objects.all()),
        "filter_categories": list(
            Category.objects.filter(parent__isnull=True)
            .prefetch_related("children")
            .order_by("order", "name_uz")
        ),
        "active_category": active_category,
        "category_slug": category_slug,
        "page_title": title,
        "query": query if query is not None else request.GET.get("q", ""),
        "is_search": query is not None,
        "current_ordering": request.GET.get("ordering", "-created_at"),
    }
    return render(request, "storefront/catalog.html", ctx)


def category_page(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    return catalog(request, category_slug=slug, title=cat.name_for(_lang()))


def search(request):
    q = request.GET.get("q", "").strip()
    return catalog(request, query=q, title=q)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category", "brand").prefetch_related("images"),
        slug=slug,
        is_active=True,
    )
    similar = list(
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .prefetch_related("images")[:8]
    )
    reviews = list(product.reviews.select_related("user").order_by("-created_at"))

    can_review = False
    already_reviewed = False
    if request.user.is_authenticated:
        already_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status__in=["paid", "shipped", "delivered"],
        ).exists()
        can_review = purchased and not already_reviewed

    ctx = {
        "product": product,
        "images": list(product.images.all()),
        "similar": similar,
        "reviews": reviews,
        "can_review": can_review,
        "already_reviewed": already_reviewed,
    }
    return render(request, "storefront/product_detail.html", ctx)


def cart_page(request):
    cart = get_or_create_cart(request)
    items = list(cart.items.select_related("product").prefetch_related("product__images"))
    ctx = {"cart": cart, "items": items, "cart_total": cart.total}
    return render(request, "storefront/cart.html", ctx)


@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    items = list(cart.items.select_related("product").prefetch_related("product__images"))
    if not items:
        return redirect("storefront:cart")

    default_address = Address.objects.filter(user=request.user, is_default=True).first()

    if request.method == "POST":
        serializer = CheckoutSerializer(data=request.POST, context={"request": request})
        if serializer.is_valid():
            order = serializer.save()
            return redirect("storefront:checkout_success", number=order.number)
        for field, errs in serializer.errors.items():
            for e in errs:
                messages.error(request, f"{field}: {e}")

    ctx = {
        "items": items,
        "cart_total": cart.total,
        "default_address": default_address,
        "addresses": list(Address.objects.filter(user=request.user)),
        "payment_methods": Order.PaymentMethod.choices,
    }
    return render(request, "storefront/checkout.html", ctx)


@login_required
def checkout_success(request, number):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"), number=number, user=request.user
    )
    return render(request, "storefront/checkout_success.html", {"order": order})


@login_required
def wishlist_page(request):
    wl, _ = Wishlist.objects.get_or_create(user=request.user)
    products = list(wl.products.filter(is_active=True).prefetch_related("images"))
    return render(request, "storefront/wishlist.html", {"products": products})


# ===========================================================================
# Auth (Django sessiya)
# ===========================================================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("storefront:account")
    form = LoginForm(request.POST or None)
    next_url = request.GET.get("next") or request.POST.get("next") or "/account/"
    # Open-redirect himoyasi: faqat o'z saytimiz ichidagi manzilga yo'naltiramiz
    if not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = "/account/"
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            auth_login(request, user)
            get_or_create_cart(request)  # mehmon savatini birlashtirish
            return redirect(next_url)
        messages.error(request, _t()["auth"]["invalid"])
    return render(request, "storefront/login.html", {"form": form, "next": next_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("storefront:account")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user = authenticate(
            request, username=user.email, password=form.cleaned_data["password"]
        )
        if user is not None:
            auth_login(request, user)
            get_or_create_cart(request)
        return redirect("storefront:account")
    return render(request, "storefront/register.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect("/")


# ===========================================================================
# Account (profil / buyurtmalar / manzillar)
# ===========================================================================
@login_required
def account(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    address_form = AddressForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "profile":
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, _t()["account"]["saved"])
                return redirect(f"{request.path}?tab=profile")
        elif action == "add_address":
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                addr = address_form.save(commit=False)
                addr.user = user
                addr.save()
                return redirect(f"{request.path}?tab=addresses")
        elif action == "delete_address":
            Address.objects.filter(pk=request.POST.get("address_id"), user=user).delete()
            return redirect(f"{request.path}?tab=addresses")
        elif action == "set_default":
            addr = Address.objects.filter(pk=request.POST.get("address_id"), user=user).first()
            if addr:
                addr.is_default = True
                addr.save()
            return redirect(f"{request.path}?tab=addresses")

    orders = list(
        Order.objects.filter(user=user).prefetch_related("items").order_by("-created_at")
    )
    ctx = {
        "profile_form": profile_form,
        "address_form": address_form,
        "orders": orders,
        "addresses": list(Address.objects.filter(user=user).order_by("-is_default")),
        "active_tab": request.GET.get("tab", "profile"),
    }
    return render(request, "storefront/account.html", ctx)


# ===========================================================================
# JSON action endpointlari (vanilla JS uchun)
# ===========================================================================
def _som(value) -> str:
    """1234567 -> '1 234 567 so'm' (joriy tilda)."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = 0
    return f"{n:,}".replace(",", " ") + " " + _t()["common"]["som"]


def _cart_payload(request, cart, opened=True, extra=None):
    agg = cart.items.aggregate(n=Sum("quantity"))
    items = list(cart.items.select_related("product").prefetch_related("product__images"))
    html = render_to_string(
        "storefront/partials/_drawer_items.html",
        {"items": items, "cart": cart, "cart_total": cart.total},
        request=request,
    )
    payload = {
        "ok": True,
        "count": int(agg["n"] or 0),
        "total": str(cart.total),
        "total_fmt": _som(cart.total),
        "html": html,
        "open": opened,
    }
    if extra:
        payload.update(extra)
    return JsonResponse(payload)


@require_POST
def cart_add(request):
    cart = get_or_create_cart(request)
    product = Product.objects.filter(pk=request.POST.get("product_id"), is_active=True).first()
    if not product:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    try:
        qty = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        qty = 1

    if product.stock <= 0:
        return _cart_payload(request, cart, opened=False)  # tugagan — savat o'zgarmaydi

    item = cart.items.filter(product=product).first()
    if item:
        item.quantity = min(item.quantity + qty, product.stock)
        item.save()
    else:
        cart.items.create(product=product, quantity=min(qty, product.stock))
    return _cart_payload(request, cart)


@require_POST
def cart_update(request):
    cart = get_or_create_cart(request)
    item = cart.items.filter(pk=request.POST.get("item_id")).select_related("product").first()
    if not item:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    try:
        qty = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        qty = 1
    removed = False
    if qty <= 0 or item.product.stock <= 0:
        item.delete()
        removed = True
        subtotal_fmt = _som(0)
        new_qty = 0
    else:
        item.quantity = min(qty, item.product.stock)
        item.save()
        new_qty = item.quantity
        subtotal_fmt = _som(item.subtotal)
    return _cart_payload(
        request,
        cart,
        opened=False,
        extra={"removed": removed, "item_subtotal_fmt": subtotal_fmt, "item_qty": new_qty},
    )


@require_POST
def cart_remove(request):
    cart = get_or_create_cart(request)
    cart.items.filter(pk=request.POST.get("item_id")).delete()
    return _cart_payload(request, cart, opened=False, extra={"removed": True})


def cart_drawer(request):
    cart = get_or_create_cart(request)
    return _cart_payload(request, cart, opened=False)


@require_POST
def wishlist_toggle(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "auth": False, "login_url": "/login/"}, status=401)
    product = Product.objects.filter(pk=request.POST.get("product_id"), is_active=True).first()
    if not product:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    wl, _ = Wishlist.objects.get_or_create(user=request.user)
    if wl.products.filter(pk=product.pk).exists():
        wl.products.remove(product)
        in_wishlist = False
    else:
        wl.products.add(product)
        in_wishlist = True
    return JsonResponse({"ok": True, "in_wishlist": in_wishlist})


@login_required
@require_POST
def review_create(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, "Siz allaqachon sharh qoldirgansiz.")
        return redirect("storefront:product", slug=slug)

    purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=["paid", "shipped", "delivered"],
    ).exists()
    if not purchased:
        messages.error(request, "Faqat ushbu mahsulotni sotib olganlar sharh yozadi.")
        return redirect("storefront:product", slug=slug)

    try:
        rating = max(1, min(5, int(request.POST.get("rating", 5))))
    except (TypeError, ValueError):
        rating = 5
    text = request.POST.get("text", "").strip()
    if not text:
        messages.error(request, _t()["common"]["error"])
        return redirect("storefront:product", slug=slug)
    Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        text=text,
        is_verified=True,
    )
    agg = product.reviews.aggregate(avg=Avg("rating"))
    product.rating = round(agg["avg"] or 0, 2)
    product.reviews_count = product.reviews.count()
    product.save(update_fields=["rating", "reviews_count"])
    messages.success(request, _t()["product"]["reviewThanks"])
    return redirect("storefront:product", slug=slug)


def search_suggest(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"results": []})
    lang = _lang()
    products = (
        Product.objects.filter(is_active=True)
        .filter(
            Q(name_uz__icontains=q)
            | Q(name_ru__icontains=q)
            | Q(name_en__icontains=q)
            | Q(brand__name_uz__icontains=q)
        )
        .prefetch_related("images")[:6]
    )
    results = []
    for p in products:
        img = p.images.all().first()
        results.append(
            {
                "name": p.name_for(lang),
                "slug": p.slug,
                "price": f"{int(p.final_price):,}".replace(",", " "),
                "image": (img.src if img else ""),
            }
        )
    return JsonResponse({"results": results})


# ===========================================================================
# Xato sahifalari
# ===========================================================================
def handler404(request, exception=None):
    return render(request, "storefront/404.html", status=404)


def handler500(request):
    return render(request, "storefront/500.html", status=500)
