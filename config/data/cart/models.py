from typing import TYPE_CHECKING
from django.db import models

from common.models import TimeStampModel
from django.contrib import admin

if TYPE_CHECKING:
    from data.cartitem.models import CartItem

# Create your models here.


class Cart(TimeStampModel):
    user = models.ForeignKey(
        "bot.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
    )

    status = models.CharField(
        choices=[
            ("ORDERING", "Buyurtma berilmoqda"),
            ("PENDING", "Buyurtma berilmoqda"),
        ],
        default="ORDERING",
        max_length=255,
    )

    items: "models.QuerySet[CartItem]"

    class Meta:
        ordering = ["-created_at"]

    class Admin(admin.ModelAdmin):

        list_display = ["user", "status"]

        list_filter = ["status"]
