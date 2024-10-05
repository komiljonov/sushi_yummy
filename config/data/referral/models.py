from django.db import models

from bot.models import User
from common.models import TimeStampModel


# Create your models here.

class Referral(TimeStampModel):
    name = models.CharField(max_length=255)

    users: "models.QuerySet[User]"
