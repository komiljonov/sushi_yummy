from typing import TYPE_CHECKING
from django.db import models
from common.models import TimeStampModel
from django.contrib import admin


if TYPE_CHECKING:
    from data.cart.models import Cart
    from data.filial.models import Filial


# Create your models here.


class PaymentType(TimeStampModel):

    code = models.CharField(max_length=255)

    name = models.CharField(max_length=255)

    iiko_id = models.CharField(max_length=255)

    filial: "Filial" = models.ForeignKey(
        "filial.Filial",
        on_delete=models.SET_NULL,
        null=True,
        related_name="payment_types",
    )

    def __str__(self):

        return f"{self.name} {self.code}"


class Payment(TimeStampModel):
    user = models.ForeignKey(
        "bot.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    provider = models.CharField(
        choices=[
            ("CLICK", "Click"),
            ("PAYME", "Payme"),
            ("CASH", "Naqd"),
        ],
        max_length=255,
    )

    amount = models.BigIntegerField()

    status = models.CharField(
        choices=[
            ("SUCCESSFUL", "Muvaffaqiyatli"),
            ("CANCELLED", "Bekor qilindi"),
        ],
        max_length=255,
        default="SUCCESSFUL",
    )

    data = models.JSONField(null=True, blank=True)

    order: "Cart"

    class Admin(admin.ModelAdmin):
        list_display = ["provider", "amount", "status", "id"]

        list_filter = ["provider", "amount", "id"]
