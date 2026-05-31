import pytest

from apps.orders.models import Order, OrderItem

pytestmark = pytest.mark.django_db


def _auth(api, user):
    res = api.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": "StrongPass123"},
        format="json",
    )
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")


def test_product_feeds(api, product):
    product.is_featured = True
    product.save()
    assert api.get("/api/v1/products/featured/").status_code == 200
    assert api.get("/api/v1/products/new/").status_code == 200
    assert api.get("/api/v1/products/bestsellers/").status_code == 200


def test_categories_tree(api, category):
    res = api.get("/api/v1/categories/")
    assert res.status_code == 200
    assert res.data["count"] == 1


def test_wishlist_add_and_list(api, user, product):
    _auth(api, user)
    add = api.post(f"/api/v1/wishlist/{product.id}/")
    assert add.status_code == 201
    lst = api.get("/api/v1/wishlist/")
    assert lst.status_code == 200
    assert len(lst.data) == 1
    rm = api.delete(f"/api/v1/wishlist/{product.id}/")
    assert rm.status_code == 204


def test_review_requires_purchase(api, user, product):
    _auth(api, user)
    res = api.post(
        f"/api/v1/products/{product.slug}/reviews/",
        {"rating": 5, "text": "Zo'r"},
        format="json",
    )
    assert res.status_code == 403  # sotib olmagan


def test_review_after_purchase_updates_rating(api, user, product):
    _auth(api, user)
    order = Order.objects.create(
        user=user, status="delivered", payment_method="click",
        full_name="B", phone="1", region="T", city="T", street="S",
    )
    OrderItem.objects.create(
        order=order, product=product, product_name=product.name_uz,
        price=product.price, quantity=1,
    )
    res = api.post(
        f"/api/v1/products/{product.slug}/reviews/",
        {"rating": 4, "text": "Yaxshi"},
        format="json",
    )
    assert res.status_code == 201
    product.refresh_from_db()
    assert product.reviews_count == 1
    assert float(product.rating) == 4.0


def test_payment_create_endpoint(api, user, product):
    _auth(api, user)
    api.post("/api/v1/cart/items/", {"product_id": product.id, "quantity": 1}, format="json")
    order_res = api.post(
        "/api/v1/orders/",
        {"full_name": "B", "phone": "1", "region": "T", "city": "T", "street": "S", "payment_method": "click"},
        format="json",
    )
    number = order_res.data["number"]
    res = api.post("/api/v1/payments/click/create/", {"order": number}, format="json")
    assert res.status_code == 201
    assert "payment_url" in res.data
