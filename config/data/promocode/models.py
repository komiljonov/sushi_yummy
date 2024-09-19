from django.db import models

from common.models import TimeStampModel
from django.contrib import admin

# Create your models here.


class Promocode(TimeStampModel):

    name = models.CharField(max_length=255)

    code = models.CharField(max_length=255)

    measurement = models.CharField(
        choices=[("ABSOLUTE", "Absolut"), ("PERCENT", "Foyizda")],
        max_length=255,
        default="ABSOLUTE",
    )

    amount = models.BigIntegerField()

    count = models.IntegerField()

    end_date = models.DateField(null=True, blank=True)

    is_limited = models.BooleanField(default=False)
    is_max_limited = models.BooleanField(default=False)

    min_amount = models.BigIntegerField()
    max_amount = models.BigIntegerField()

    class Admin(admin.ModelAdmin):
        list_display = [
            "code",
            "measurement",
            "amount",
            "count",
            "end_date",
            "min_amount",
            "max_amount",
        ]

        list_filter = ["measurement"]

        search_fields = ["id", "code", "measurement"]
