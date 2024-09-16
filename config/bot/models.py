from typing import TYPE_CHECKING
from django.db import models


from common.models import TimeStampModel
from telegram import Update

from utils.language import multilanguage


if TYPE_CHECKING:
    from data.cart.models import Cart
    from data.category.models import Category
    from data.product.models import Product

# Create your models here.


class User(TimeStampModel):

    chat_id = models.BigIntegerField()

    tg_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)

    lang = models.CharField(max_length=255, null=True, blank=True)

    carts: "models.QuerySet[Cart]"

    @classmethod
    def get(cls, update: Update):
        tgUser = update.effective_user

        user = cls.objects.get_or_create(
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
