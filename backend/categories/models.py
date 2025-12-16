from core.models import BaseModel
from django.db import models


class Category(BaseModel):
    telegram_id = models.BigIntegerField(
        db_index=True,
        help_text="Telegram user ID who owns this category",
    )
    name = models.CharField(
        max_length=100,
        help_text="Category name",
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["telegram_id", "name"],
                name="unique_category_per_user",
            )
        ]

    def __str__(self):
        return f"{self.name} (user: {self.telegram_id})"
