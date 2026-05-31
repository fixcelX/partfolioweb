try:
    from .celery import app as celery_app

    __all__ = ("celery_app",)
except ModuleNotFoundError:  # celery o'rnatilmagan muhit (ixtiyoriy)
    celery_app = None
