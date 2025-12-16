from categories.models import Category
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "telegram_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "telegram_id", "created_at", "updated_at"]


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
