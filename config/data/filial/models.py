from typing import TYPE_CHECKING
from django.db import models


from common.models import TimeStampModel
from django.db.models import F, Func
from telegram import Location as TgLocation

if TYPE_CHECKING:
    from bot.models import Location

class Radians(Func):
    function = "RADIANS"


# Create your models here.


class Filial(TimeStampModel):

    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)

    location: "Location" = models.ForeignKey(
        "bot.Location", on_delete=models.SET_NULL, null=True, blank=True
    )

    active = models.BooleanField(default=True)

    @classmethod
    def get_nearest_filial(cls, location: TgLocation):
        # Get all filials with a calculated distance
        filials = cls.objects.annotate(
            distance=(
                (Radians(F("location__latitude")) - Radians(location.latitude)) ** 2
                + (Radians(F("location__longitude")) - Radians(location.longitude)) ** 2
            )
        ).order_by("distance")

        # Return the nearest filial
        return filials.first()
