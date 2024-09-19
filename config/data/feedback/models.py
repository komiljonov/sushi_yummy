from typing import TYPE_CHECKING

from django.db import models

from common.models import TimeStampModel

if TYPE_CHECKING:
    from bot.models import User

# Create your models here.


class Service(TimeStampModel):

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)


class Feedback(TimeStampModel):
    user: "User" = models.ForeignKey(
        "bot.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    service: Service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True
    )

    comment = models.TextField()

    star = models.IntegerField()
