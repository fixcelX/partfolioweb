import pytest

from apps.catalog.models import Product

pytestmark = pytest.mark.django_db


def test_product_list(api, product):
    res = api.get("/api/v1/products/")
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["slug"] == product.slug


def test_product_price_filter(api, category):
    Product.objects.create(name_uz="Arzon", name_en="Cheap", category=category, price=100000, stock=5, sku="S1")
    Product.objects.create(name_uz="Qimmat", name_en="Expensive", category=category, price=5000000, stock=5, sku="S2")
    res = api.get("/api/v1/products/?min_price=1000000")
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["name"] == "Qimmat"


def test_product_search(api, category):
    Product.objects.create(name_uz="Samsung Galaxy", name_en="Samsung Galaxy", category=category, price=200000, stock=5, sku="S3")
    res = api.get("/api/v1/products/?search=Galaxy")
    assert res.data["count"] == 1


def test_localized_name_ru(api, product):
    product.name_ru = "Телефон"
    product.save()
    res = api.get(f"/api/v1/products/{product.slug}/?lang=ru")
    assert res.data["name"] == "Телефон"


def test_discount_percent(db, category):
    p = Product.objects.create(
        name_uz="Aksiya", name_en="Sale", category=category,
        price=1000000, discount_price=750000, stock=5, sku="S4",
    )
    assert p.discount_percent == 25
    assert p.final_price == 750000
