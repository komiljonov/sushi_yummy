from django.db import models
from django.contrib import admin

from common.models import NameModel

# Create your models here.


class Category(models.Model, NameModel):

    parent: "Category" = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="children"
    )

    children: "models.QuerySet[Category]"

    class admin(admin.ModelAdmin):

        list_display = [*NameModel.names_list, "parent"]

        search_fields = [*NameModel.names_list]

        list_filter = ["parent"]
