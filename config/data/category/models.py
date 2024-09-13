from django.db import models
from django.contrib import admin

from data.product.models import Product


# Create your models here.


class Category(models.Model):

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_us = models.CharField(max_length=255)

    parent: "Category" = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    children: "models.QuerySet[Category]"
    products: "models.QuerySet[Product]"

    class admin(admin.ModelAdmin):

        list_display = ["name_uz", "name_ru", "name_us", "parent"]

        search_fields = ["name_uz", "name_ru", "name_us"]

        list_filter = ["parent"]
