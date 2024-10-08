from typing import TYPE_CHECKING
from django.db import models
from common.models import TimeStampModel
from django.core.validators import MinValueValidator
from django.contrib import admin

from django.db.models import Sum

if TYPE_CHECKING:
    from data.category.models import Category
    from data.file.models import File
    from data.analytics.models import ProductVisit
    from data.cartitem.models import CartItem

# Create your models here.


class Product(TimeStampModel):

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)

    iiko_id = models.CharField(max_length=255)

    # filial = models.ForeignKey(
    #     "filial.Filial", on_delete=models.SET_NULL, null=True, blank=True
    # )

    filials = models.ManyToManyField("filial.Filial", blank=True)

    caption_uz = models.CharField(max_length=950)
    caption_ru = models.CharField(max_length=950)

    image: "File" = models.ForeignKey(
        "file.File", on_delete=models.SET_NULL, null=True, blank=True
    )

    price = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(
                0, message="Kechirasiz narx 0 dan kichik bo'lishi mumkin emas."
            )
        ],
    )

    category: "Category" = models.ForeignKey(
        "category.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    visits: "models.QuerySet[ProductVisit]"

    cart_items: "models.QuerySet[CartItem]"

    def __str__(self) -> str:
        return f"Product( {self.name_uz} )"

    class Meta:
        ordering = ["-name_uz"]

    class Admin(admin.ModelAdmin):

        list_display = ["name_uz", "name_ru", "price", "category"]

        list_filter = ["filials", "category"]

        search_fields = ["name_uz", "name_ru", "iiko_id"]

    def get_sale_count(self):
        # return 5
        return self.cart_items.filter(
            cart__status__in=[
                "PENDING_PAYMENT",
                "PENDING",
                "PENDING_KITCHEN",
                "PREPARING",
                "DELIVERING",
                "DONE",
            ]
        ).aggregate(total_count=Sum("count"))["total_count"]
