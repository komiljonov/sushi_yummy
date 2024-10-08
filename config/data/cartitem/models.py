from typing import TYPE_CHECKING
from django.db import models
from django.contrib import admin
from common.models import TimeStampModel


if TYPE_CHECKING:
    from data.product.models import Product
    from data.cart.models import Cart


# Create your models here.
class CartItem(TimeStampModel):

    cart: "Cart" = models.ForeignKey(
        "cart.Cart", on_delete=models.CASCADE, related_name="items"
    )

    product: "Product" = models.ForeignKey(
        "product.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
    )

    price = models.FloatField(default=0)

    count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Set the price to the current product price if not already set
        if not self.pk:  # If this is a new object
            self.price = self.product.price if self.product else 0
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    class Admin(admin.ModelAdmin):

        list_display = ["cart", "product", "price", "count", "created_at"]
