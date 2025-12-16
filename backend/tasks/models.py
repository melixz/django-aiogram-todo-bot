from django.db import models

from categories.models import Category
from core.models import BaseModel


class Task(BaseModel):
    telegram_id = models.BigIntegerField(
        db_index=True,
        help_text="Telegram user ID who owns this task",
    )
    title = models.CharField(
        max_length=255,
        help_text="Task title",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Task description",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        help_text="Optional category for this task",
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Due date for the task",
    )
    is_completed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the task is completed",
    )
    notification_sent = models.BooleanField(
        default=False,
        help_text="Whether notification was sent for due date",
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["telegram_id", "is_completed"]),
            models.Index(fields=["due_date", "notification_sent"]),
        ]

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.title} (user: {self.telegram_id})"
