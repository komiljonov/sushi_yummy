from typing import TYPE_CHECKING
from django.db import models


from common.models import TimeStampModel
from telegram import Update

from data.feedback.models import Service
from data.filial.models import Filial
from utils.language import multilanguage


if TYPE_CHECKING:
    from data.cart.models import Cart
    from data.category.models import Category
    from data.product.models import Product

# Create your models here.


class User(TimeStampModel):

    chat_id = models.BigIntegerField()

    name = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)

    tg_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)

    lang = models.CharField(max_length=255, null=True, blank=True)

    carts: "models.QuerySet[Cart]"
    locations: "models.QuerySet[Location]"

    @classmethod
    def get(cls, update: Update):
        tgUser = update.effective_user

        user = cls.objects.prefetch_related("carts").get_or_create(
            chat_id=tgUser.id, tg_name=tgUser.full_name, username=tgUser.username
        )[0]

        temp = user.temp if user else None

        return tgUser, user, temp, user.i18n

    @property
    def temp(self):
        return UserTemp.objects.get_or_create(user=self)[0]

    @property
    def i18n(self):
        return multilanguage.__getattr__(self.lang if self.lang else "uz")

    @property
    def cart(self):
        return self.carts.get_or_create(status="ORDERING")[0]


class UserTemp(TimeStampModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    category: "Category" = models.ForeignKey(
        "category.Category", on_delete=models.SET_NULL, null=True, blank=True
    )

    product: "Product" = models.ForeignKey(
        "product.Product", on_delete=models.SET_NULL, null=True, blank=True
    )

    location: "Location" = models.ForeignKey(
        "bot.Location", on_delete=models.SET_NULL, null=True, blank=True
    )

    filial: "Filial" = models.ForeignKey(
        "filial.Filial", on_delete=models.SET_NULL, null=True, blank=True
    )

    cmid = models.IntegerField(null=True, blank=True)
    cmid2 = models.IntegerField(null=True, blank=True)

    time = models.DateTimeField(null=True, blank=True)

    star = models.IntegerField(null=True, blank=True)
    service: "Service" = models.ForeignKey(
        "feedback.Service", on_delete=models.SET_NULL, null=True, blank=True
    )


class Location(TimeStampModel):

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="locations"
    )

    name = models.CharField(max_length=500)

    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField(null=True, blank=True)

    used = models.BooleanField(default=False)
    special = models.BooleanField(default=False)
