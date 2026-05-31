from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Faqat egasi o'zgartira oladi; o'qish hammaga ochiq."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, "user", None)
        return owner == request.user


class IsSellerOrAdmin(permissions.BasePermission):
    """Sotuvchi yoki admin rollari uchun."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role in ("seller", "admin")
        )
