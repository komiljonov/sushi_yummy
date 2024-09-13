from typing import Any
from uuid import uuid4
from django.db import models
from django.contrib import admin
from django.utils import timezone
from django.contrib import admin

from simple_history.models import HistoricalRecords

# Create your models here.


class TimeStampModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords(inherit=True)

    # Custom manager for soft delete
    class SoftDeleteManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted_at__isnull=True)

    objects = SoftDeleteManager()
    all_objects = (
        models.Manager()
    )  # Manager to access all objects, including deleted ones

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.save()

    class CustomFilter(admin.SimpleListFilter):

        title = "Deleted or not filter"
        parameter_name = "deleted"

        def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
            return [
                ("deleted", "O'chirilgan"),
                ("not_deleted", "O'chirilmagan"),
            ]

        def queryset(
            self, request: Any, queryset: models.QuerySet[Any]
        ) -> models.QuerySet[Any] | None:
            if self.value() == "deleted":
                return queryset.exclude(deleted_at=None)

            if self.value() == "not_deleted":
                return queryset.filter(deleted_at=None)

            return queryset

