import math
from typing import TYPE_CHECKING
from django.db import models


from common.models import TimeStampModel
from django.db.models import F, FloatField, ExpressionWrapper, Func

from telegram import Location as TgLocation


if TYPE_CHECKING:
    from bot.models import Location


class Radians(Func):
    function = "RADIANS"


class Sin(Func):
    function = "SIN"


class Cos(Func):
    function = "COS"


class Sqrt(Func):
    function = "SQRT"


class Pow(Func):
    function = "POW"


# Create your models here.


class Filial(TimeStampModel):

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)

    location: "Location" = models.ForeignKey(
        "bot.Location", on_delete=models.SET_NULL, null=True, blank=True
    )

    active = models.BooleanField(default=True)

    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        R = 6371  # Radius of Earth in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def get_nearest_filial(cls, location: "Location"):
        # Get all active filials with their locations
        active_filials = cls.objects.filter(active=True).select_related("location")

        nearest_filial = None
        min_distance = float("inf")

        for filial in active_filials:
            if filial.location:
                distance = cls.haversine(
                    location.longitude,
                    location.latitude,
                    filial.location.longitude,
                    filial.location.latitude,
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_filial = filial

        return nearest_filial
