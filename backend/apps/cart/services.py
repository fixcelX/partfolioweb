from .models import Cart


def get_or_create_cart(request) -> Cart:
    """Auth bo'lsa user saviti, aks holda sessiya saviti.

    Login bo'lganda anonim savat user savatiga birlashtiriladi (guest merge).
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        _merge_session_cart(request, cart)
        return cart

    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key, user__isnull=True
    )
    return cart


def _merge_session_cart(request, user_cart: Cart) -> None:
    session_key = request.session.session_key
    if not session_key:
        return
    guest_cart = (
        Cart.objects.filter(session_key=session_key, user__isnull=True)
        .exclude(pk=user_cart.pk)
        .first()
    )
    if not guest_cart:
        return
    for item in guest_cart.items.all():
        existing = user_cart.items.filter(product=item.product).first()
        if existing:
            existing.quantity = min(
                existing.quantity + item.quantity, item.product.stock
            )
            existing.save()
        else:
            item.cart = user_cart
            item.save()
    guest_cart.delete()
