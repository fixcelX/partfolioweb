from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_order_confirmation(order_number: str, email: str) -> None:
    """Buyurtma tasdig'i (dev'da console backend)."""
    send_mail(
        subject=f"ZAMON MARKET — buyurtma {order_number} qabul qilindi",
        message=(
            f"Rahmat! Buyurtmangiz {order_number} muvaffaqiyatli qabul qilindi "
            f"va to'lov tasdiqlandi. Holatni profilingizda kuzating."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
