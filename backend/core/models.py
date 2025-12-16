from django.db import models
from django_ulid.models import ULIDField, default


class BaseModel(models.Model):
    id = ULIDField(default=default, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
