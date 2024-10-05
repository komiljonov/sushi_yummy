from django.db import models

from common.models import TimeStampModel

# Create your models here.


class Taxi(TimeStampModel):
    order_id = models.IntegerField()

    state_id = models.IntegerField()
    state_kind = models.CharField(max_length=255)

    crew_id = models.IntegerField(null=True, blank=True)

    car_id = models.IntegerField(null=True, blank=True)
    start_time = models.BigIntegerField(null=True, blank=True)
    sourcetime = models.BigIntegerField(null=True, blank=True)

    source_lat = models.FloatField(null=True, blank=True)
    source_lon = models.FloatField(null=True, blank=True)

    destination_lat = models.FloatField(null=True, blank=True)
    destination_lon = models.FloatField(null=True, blank=True)

    phone = models.CharField(max_length=255)

    client_id = models.IntegerField(null=True, blank=True)

    sum = models.FloatField(null=True, blank=True)
    total_sum = models.FloatField(null=True, blank=True)

    car_mark = models.CharField(max_length=255, null=True, blank=True)
    car_model = models.CharField(max_length=255, null=True, blank=True)
    car_color = models.CharField(max_length=255, null=True, blank=True)
    car_number = models.CharField(max_length=255, null=True, blank=True)

    driver_phone_number = models.CharField(max_length=255, null=True, blank=True)
