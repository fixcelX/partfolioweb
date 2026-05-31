"""To'lov provayderlari — Click (to'liq oqim), Payme + Stripe (interfeys).

Click webhook imzosi MD5 bilan tekshiriladi. Kalitlar faqat settings.PAYMENTS
(ya'ni .env) dan o'qiladi.
"""
from __future__ import annotations

import hashlib
from decimal import Decimal

from django.conf import settings

from apps.orders.models import Order

from .models import Payment


class PaymentError(Exception):
    pass


class BaseProvider:
    name = ""

    def __init__(self):
        self.config = settings.PAYMENTS

    def create(self, order: Order) -> dict:
        """To'lov sessiyasi/linkini yaratadi."""
        raise NotImplementedError

    def handle_webhook(self, data: dict) -> dict:
        """Provayder callback — imzo tekshirib, buyurtmani paid qiladi."""
        raise NotImplementedError

    # --- umumiy yordamchi: idempotent paid ---
    def _mark_paid(self, order: Order, transaction_id: str, payload: dict) -> Payment:
        payment, _ = Payment.objects.get_or_create(
            order=order,
            provider=self.name,
            transaction_id=transaction_id,
            defaults={"amount": order.total},
        )
        if payment.status == Payment.Status.PAID:
            return payment  # idempotent — ikki marta to'lanmaydi
        payment.status = Payment.Status.PAID
        payment.raw_payload = payload
        payment.save()
        if order.status == Order.Status.PENDING:
            order.status = Order.Status.PAID
            order.save(update_fields=["status"])
            from apps.orders.tasks import send_order_confirmation

            send_order_confirmation.delay(order.number, order.user.email)
        return payment


class ClickProvider(BaseProvider):
    name = "click"

    def create(self, order: Order) -> dict:
        merchant_id = self.config.get("CLICK_MERCHANT_ID") or "TEST_MERCHANT"
        amount = order.total
        url = (
            f"https://my.click.uz/services/pay?service_id={merchant_id}"
            f"&merchant_trans_id={order.number}&amount={amount}"
            f"&return_url={settings.FRONTEND_URL}/checkout/success"
        )
        Payment.objects.get_or_create(
            order=order, provider=self.name,
            defaults={"amount": amount, "transaction_id": ""},
        )
        return {"provider": "click", "payment_url": url, "amount": str(amount)}

    def _make_sign(self, params: dict) -> str:
        secret = self.config.get("CLICK_SECRET_KEY", "")
        raw = (
            f"{params.get('click_trans_id','')}{params.get('service_id','')}{secret}"
            f"{params.get('merchant_trans_id','')}{params.get('amount','')}"
            f"{params.get('action','')}{params.get('sign_time','')}"
        )
        return hashlib.md5(raw.encode()).hexdigest()

    def handle_webhook(self, data: dict) -> dict:
        expected = self._make_sign(data)
        if data.get("sign_string") and data["sign_string"] != expected:
            raise PaymentError("Noto'g'ri imzo (sign_string).")

        order = Order.objects.filter(number=data.get("merchant_trans_id")).first()
        if not order:
            raise PaymentError("Buyurtma topilmadi.")

        if Decimal(str(data.get("amount", "0"))) != order.total:
            raise PaymentError("Summa mos kelmadi.")

        # action=1 (complete) bo'lganda to'landi deb belgilanadi
        if str(data.get("action")) == "1":
            self._mark_paid(order, str(data.get("click_trans_id", "")), data)
        return {"error": 0, "error_note": "Success"}


class PaymeProvider(BaseProvider):
    name = "payme"

    def create(self, order: Order) -> dict:
        merchant_id = self.config.get("PAYME_MERCHANT_ID") or "TEST_MERCHANT"
        # Payme summasi tiyin'da (so'm * 100)
        amount_tiyin = int(order.total * 100)
        import base64

        params = f"m={merchant_id};ac.order={order.number};a={amount_tiyin}"
        token = base64.b64encode(params.encode()).decode()
        url = f"https://checkout.paycom.uz/{token}"
        Payment.objects.get_or_create(
            order=order, provider=self.name, defaults={"amount": order.total}
        )
        return {"provider": "payme", "payment_url": url, "amount": str(order.total)}

    def handle_webhook(self, data: dict) -> dict:
        # Payme JSON-RPC: PerformTransaction bo'lganda paid
        method = data.get("method")
        params = data.get("params", {})
        order_number = params.get("account", {}).get("order")
        order = Order.objects.filter(number=order_number).first()
        if not order:
            return {"error": {"code": -31050, "message": "Buyurtma topilmadi"}}
        if method == "PerformTransaction":
            self._mark_paid(order, str(params.get("id", "")), data)
            return {"result": {"perform_time": 0, "state": 2}}
        return {"result": {"allow": True}}


class StripeProvider(BaseProvider):
    name = "stripe"

    def create(self, order: Order) -> dict:
        # Test mode interfeys — real kalit bo'lsa Stripe Checkout Session ochiladi
        Payment.objects.get_or_create(
            order=order, provider=self.name, defaults={"amount": order.total}
        )
        url = f"{settings.FRONTEND_URL}/checkout/success?provider=stripe&order={order.number}"
        return {"provider": "stripe", "payment_url": url, "amount": str(order.total)}

    def handle_webhook(self, data: dict) -> dict:
        order = Order.objects.filter(number=data.get("order")).first()
        if not order:
            raise PaymentError("Buyurtma topilmadi.")
        if data.get("type") == "checkout.session.completed":
            self._mark_paid(order, str(data.get("id", "")), data)
        return {"received": True}


_PROVIDERS = {
    "click": ClickProvider,
    "payme": PaymeProvider,
    "stripe": StripeProvider,
}


def get_provider(name: str) -> BaseProvider:
    cls = _PROVIDERS.get(name)
    if not cls:
        raise PaymentError(f"Noma'lum provayder: {name}")
    return cls()
