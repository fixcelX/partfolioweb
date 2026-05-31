import pytest

from apps.orders.models import Order
from apps.payments.providers import ClickProvider

pytestmark = pytest.mark.django_db


def _auth(api, user):
    res = api.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": "StrongPass123"},
        format="json",
    )
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def test_add_to_cart(api, user, product):
    _auth(api, user)
    res = api.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 2}, format="json")
    assert res.status_code == 201
    assert res.data["total_quantity"] == 2


def test_cart_rejects_over_stock(api, user, product):
    _auth(api, user)
    res = api.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 999}, format="json")
    assert res.status_code == 400


def test_checkout_reduces_stock_atomically(api, user, product):
    _auth(api, user)
    api.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 3}, format="json")
    res = api.post(
        "/api/v1/orders/",
        {
            "full_name": "Buyer", "phone": "+998901112233",
            "region": "Toshkent", "city": "Toshkent", "street": "Mustaqillik 1",
            "payment_method": "click",
        },
        format="json",
    )
    assert res.status_code == 201
    assert res.data["number"].startswith("UZM-")
    product.refresh_from_db()
    assert product.stock == 7  # 10 - 3
    assert product.sold_count == 3


def test_payment_webhook_idempotent(api, user, product):
    _auth(api, user)
    api.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
    order_res = api.post(
        "/api/v1/orders/",
        {"full_name": "B", "phone": "1", "region": "T", "city": "T", "street": "S", "payment_method": "click"},
        format="json",
    )
    order = Order.objects.get(number=order_res.data["number"])

    provider = ClickProvider()
    payload = {
        "action": "1", "click_trans_id": "TX123",
        "merchant_trans_id": order.number, "amount": str(order.total),
    }
    provider.handle_webhook(payload)
    provider.handle_webhook(payload)  # ikkinchi marta — idempotent

    order.refresh_from_db()
    assert order.status == Order.Status.PAID
    assert order.payments.filter(status="paid").count() == 1
