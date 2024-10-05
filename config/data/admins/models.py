from django.contrib.auth.models import AbstractUser

from django.db import models

# Create your models here.



class CustomUser(AbstractUser):

    filial = models.ForeignKey("filial.Filial",on_delete=models.SET_NULL, null=True,blank=True,related_name="users")

    role = models.CharField(choices=[
        ("ADMIN","Admin"),
        ("CASHIER", "Kassir"),
        ("CHEF","Oshpaz")
    ], default="ADMIN")

    def __str__(self):
        return f"{self.username} ({self.filial})"


