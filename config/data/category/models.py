from django.db import models
from django.contrib import admin

from common.models import TimeStampModel
from data.product.models import Product


# Create your models here.


class Category(TimeStampModel):

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    # name_us = models.CharField(max_length=255)

    parent: "Category" = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    children: "models.QuerySet[Category]"
    products: "models.QuerySet[Product]"

    class Meta:
        ordering = ["-created_at"]

    class Admin(admin.ModelAdmin):

        list_display = ["name_uz", "name_ru", "parent"]

        search_fields = ["name_uz", "name_ru"]

        list_filter = ["parent"]
