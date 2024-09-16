from django.db import models

from common.models import TimeStampModel

# Create your models here.


class File(TimeStampModel):

    file = models.FileField(upload_to="uploads")

    filename = models.CharField(max_length=255)
