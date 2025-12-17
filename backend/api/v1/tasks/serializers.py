from rest_framework import serializers
from tasks.models import Task


class CategoryListSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class TaskSerializer(serializers.ModelSerializer):
    category_detail = CategoryListSerializer(source="category", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "telegram_id",
            "category",
            "category_detail",
            "due_date",
            "is_completed",
            "notification_sent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "telegram_id",
            "notification_sent",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "category" in data:
            del data["category"]
        if data.get("category_detail"):
            data["category"] = data.pop("category_detail")
        else:
            data["category"] = None
            data.pop("category_detail", None)
        return data


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "category",
            "due_date",
        ]

    def validate_category(self, value):
        if value is None:
            return value

        telegram_id = self.context.get("telegram_id")
        if telegram_id and value.telegram_id != telegram_id:
            raise serializers.ValidationError("Category does not belong to this user.")
        return value


class TaskListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "category_name",
            "due_date",
            "is_completed",
            "created_at",
        ]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
