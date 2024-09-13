from typing import TYPE_CHECKING
from django.db import models
from common.models import TimeStampModel, NameModel, CaptionModel
from django.contrib import admin
from django.core.validators import MinValueValidator


if TYPE_CHECKING:
    from category.models import Category

# Create your models here.


class Product(TimeStampModel, NameModel, CaptionModel):

    image = models.ImageField(upload_to="")

    price = models.FloatField(
        default=0,
        validators=[
            MinValueValidator(0, "Kechirasiz narx 0 dan kichik bo'lishi mumkin emas.")
        ],
    )

    category: "Category" = models.ForeignKey(
        "category.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )