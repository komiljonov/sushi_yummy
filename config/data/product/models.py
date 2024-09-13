from typing import TYPE_CHECKING
from django.db import models
from common.models import TimeStampModel
from django.core.validators import MinValueValidator


if TYPE_CHECKING:
    from category.models import Category

# Create your models here.


class Product(TimeStampModel):

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_us = models.CharField(max_length=255)

    caption_uz = models.CharField(max_length=255)
    caption_ru = models.CharField(max_length=255)
    caption_us = models.CharField(max_length=255)

    image = models.ImageField(upload_to="")

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
