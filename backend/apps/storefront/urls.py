"""Storefront web yo'nalishlari (root domen ostida)."""
from django.urls import path

from . import views

app_name = "storefront"

urlpatterns = [
    path("", views.home, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("category/<slug:slug>/", views.category_page, name="category"),
    path("search/", views.search, name="search"),
    path("product/<slug:slug>/", views.product_detail, name="product"),
    path("product/<slug:slug>/review/", views.review_create, name="review_create"),
    path("cart/", views.cart_page, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/<str:number>/", views.checkout_success, name="checkout_success"),
    path("wishlist/", views.wishlist_page, name="wishlist"),
    path("account/", views.account, name="account"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    # JSON action endpointlari (vanilla JS)
    path("actions/cart/add/", views.cart_add, name="cart_add"),
    path("actions/cart/update/", views.cart_update, name="cart_update"),
    path("actions/cart/remove/", views.cart_remove, name="cart_remove"),
    path("actions/cart/drawer/", views.cart_drawer, name="cart_drawer"),
    path("actions/wishlist/toggle/", views.wishlist_toggle, name="wishlist_toggle"),
    path("actions/search/", views.search_suggest, name="search_suggest"),
]
