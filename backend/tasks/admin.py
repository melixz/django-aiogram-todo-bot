from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "telegram_id",
        "category",
        "due_date",
        "is_completed",
        "notification_sent",
        "created_at",
    ]
    list_filter = ["is_completed", "notification_sent", "created_at", "due_date"]
    search_fields = ["title", "description", "telegram_id"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
    raw_id_fields = ["category"]
    list_editable = ["is_completed"]

    fieldsets = [
        (None, {"fields": ["id", "title", "description", "telegram_id"]}),
        ("Category", {"fields": ["category"]}),
        (
            "Status",
            {"fields": ["is_completed", "due_date", "notification_sent"]},
        ),
        ("Timestamps", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("category")
