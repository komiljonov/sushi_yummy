from django.db import models

from common.models import TimeStampModel
from django.contrib import admin

# Create your models here.


class Promocode(TimeStampModel):

    code = models.CharField(max_length=255)

    measurement = models.CharField(
        choices=[("ABSOLUTE", "Absolut"), ("PERCENT", "Foyizda")],
        max_length=255,
        default="ABSOLUTE",
    )

    amount = models.BigIntegerField(null=True, blank=True)

    percent = models.FloatField(null=True, blank=True)

    count = models.IntegerField()

    class Admin(admin.ModelAdmin):
        list_display = ["code", "measurement", "amount", "percent", "count"]

        list_filter = ["measurement"]

        search_fields = ["id", "code", "measurement"]
