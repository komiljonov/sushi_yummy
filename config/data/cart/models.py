from typing import TYPE_CHECKING
from django.db import models

from common.models import TimeStampModel
from django.contrib import admin

if TYPE_CHECKING:
    from data.cartitem.models import CartItem
    from bot.models import User

# Create your models here.


class Cart(TimeStampModel):
    user: "User" = models.ForeignKey(
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
    
    
    def __str__(self) -> str:
        return f"Cart( {self.user.tg_name} )"

    class Meta:
        ordering = ["-created_at"]

    class Admin(admin.ModelAdmin):

        list_display = ["user", "status"]

        list_filter = ["status"]
