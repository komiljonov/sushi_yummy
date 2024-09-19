from django.db import models
from common.models import TimeStampModel
from django.contrib import admin

# Create your models here.


class Payment(TimeStampModel):

    user = models.ForeignKey(
        "bot.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    provider = models.CharField(
        choices=[
            ("CLICK", "Click"),
            ("PAYME", "Payme"),
            ("CASH", "Naqd"),
        ],
        max_length=255,
    )

    amount = models.BigIntegerField()

    status = models.CharField(
        choices=[
            ("SUCCESSFUL", "Muvaffaqiyatli"),
            ("CANCELLED", "Bekor qilindi"),
        ],
        max_length=255,
        default="SUCCESSFUL",
    )
    
    
    data = models.JSONField(null=True,blank=True)

    class Admin(admin.ModelAdmin):

        list_display = ["provider", "amount", "status", "id"]

        list_filter = ["provider", "amount", "id"]
