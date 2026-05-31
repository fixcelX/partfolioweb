from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("id", "user_name", "rating", "text", "is_verified", "created_at")
        read_only_fields = ("is_verified",)

    def get_user_name(self, obj) -> str:
        return obj.user.first_name or obj.user.email.split("@")[0]
