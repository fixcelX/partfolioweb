import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.catalog.models import Category, Product


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """Har test oldidan/keyin throttle hisobini tozalash."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        email="buyer@test.uz", password="StrongPass123", first_name="Buyer"
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name_uz="Elektronika", name_en="Electronics")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name_uz="Telefon", name_en="Phone", category=category,
        price=1000000, stock=10, sku="SKU-TEST-1",
    )
