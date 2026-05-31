import pytest

pytestmark = pytest.mark.django_db


def test_register_returns_tokens(api):
    res = api.post(
        "/api/v1/auth/register/",
        {
            "email": "new@test.uz",
            "first_name": "New",
            "password": "StrongPass123",
            "password2": "StrongPass123",
        },
        format="json",
    )
    assert res.status_code == 201
    assert "access" in res.data and "refresh" in res.data
    assert res.data["user"]["email"] == "new@test.uz"


def test_register_password_mismatch(api):
    res = api.post(
        "/api/v1/auth/register/",
        {
            "email": "x@test.uz",
            "password": "StrongPass123",
            "password2": "Different123",
        },
        format="json",
    )
    assert res.status_code == 400


def test_login_and_me(api, user):
    res = api.post(
        "/api/v1/auth/login/",
        {"email": user.email, "password": "StrongPass123"},
        format="json",
    )
    assert res.status_code == 200
    token = res.data["access"]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    me = api.get("/api/v1/auth/me/")
    assert me.status_code == 200
    assert me.data["email"] == user.email
