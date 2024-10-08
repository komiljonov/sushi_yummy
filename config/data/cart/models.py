from typing import TYPE_CHECKING, Literal
from django.db import models

from bot.models import Location
from common.models import TimeStampModel
from django.contrib import admin

from data.filial.models import Filial
from django.db.models import F, Sum

from data.payment.models import Payment
from data.promocode.models import Promocode

if TYPE_CHECKING:
    from data.cartitem.models import CartItem
    from bot.models import User
    from bot.models import Location
    from data.filial.models import Filial
    from utils.iiko import Iiko


# Create your models here.


class Cart(TimeStampModel):
    user: "User" = models.ForeignKey(
        "bot.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
    )

    order_id = models.IntegerField(unique=True, blank=True, null=True)

    iiko_id = models.CharField(max_length=255, null=True, blank=True)
    correlation_id = models.CharField(max_length=255, null=True, blank=True)

    phone_number = models.CharField(max_length=255, null=True, blank=True)

    comment = models.CharField(max_length=1024, null=True, blank=True)

    promocode: "Promocode" = models.ForeignKey(
        "promocode.Promocode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    payment: "Payment" = models.OneToOneField(
        "payment.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
    )

    status = models.CharField(
        choices=[
            ("ORDERING", "Buyurtma berilmoqda"),
            ("PENDING_PAYMENT", "To'lov kutilmoqda"),
            ("PENDING", "Kutilmoqda"),
            ("PENDING_KITCHEN", "Tayyorlanishi kutilmoqda"),
            ("PREPARING", "Tayyorlanmoqda"),
            ("DELIVERING", "Yetkazilmoqda"),
            ("DONE", "Tugadi"),
            ("CANCELLED", "Bekor qilindi."),
        ],
        default="ORDERING",
        max_length=255,
    )

    delivery: Literal["DELIVER","TAKEAWAY"] = models.CharField(
        choices=[("DELIVER", "Yetkazib berish"), ("TAKEAWAY", "Olib ketish")],
        max_length=255,
        default="DELIVER",
    )

    time = models.DateTimeField(null=True, blank=True)

    filial: "Filial" = models.ForeignKey(
        "filial.Filial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    location: "Location" = models.ForeignKey(
        "bot.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    order_time = models.DateTimeField(null=True, blank=True)

    taxi = models.ForeignKey(
        "taxi.Taxi", on_delete=models.SET_NULL, null=True, blank=True
    )

    items: "models.QuerySet[CartItem]"

    # def save(self, *args, **kwargs):
    #     if self.order_id is None:
    #         # Fetch the last entry with a valid (non-None) order_id
    #         last_entry = (
    #             Cart.all_objects.exclude(order_id__isnull=True)
    #             .order_by("-order_id")
    #             .first()
    #         )

    #         if last_entry:
    #             # If there is a valid order_id, increment from the last one
    #             self.order_id = last_entry.order_id + 1
    #         else:
    #             # If no valid order_id found, start from 111111
    #             self.order_id = 111111

    #     super(Cart, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Cart( {self.user.tg_name if self.user else "Anonym"} )"

    class Meta:
        ordering = ["-created_at"]

    class Admin(admin.ModelAdmin):

        list_display = ["user", "status", "order_id"]

        list_filter = ["status"]

    @property
    def price(self):
        return self.items.annotate(t_price=F("count") * F("price")).aggregate(
            total_price=Sum("t_price")
        )["total_price"] or 0

    @property
    def discount_price(self):

        if self.promocode is None:
            return self.price

        # return self.price - ((self.price // 100) * 20)

        if self.promocode.measurement == "PERCENT":
            return self.price - ((self.price // 100) * self.promocode.amount)

        return self.price - self.promocode.amount

    @property
    def saving(self):
        if self.promocode is None:
            return 0

        return self.price - self.discount_price

    def order(self, manager: "Iiko"):

        success = manager.create_order(self)

        return True

    def get_payment_type(self):

        if self.payment is None:
            return None

        if self.payment.provider == "CLICK":
            return self.filial.click_payment_type

        if self.payment.provider == "PAYME":
            return self.filial.payme_payment_type

        if self.payment.provider == "CASH":
            return self.filial.cash_payment_type
