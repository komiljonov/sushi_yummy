from typing import TYPE_CHECKING
from django.db import models

from common.models import TimeStampModel
from django.utils import timezone
from datetime import timedelta
from django.contrib import admin

if TYPE_CHECKING:
    from bot.models import User
    from data.category.models import Category
    from data.product.models import Product

# Create your models here.

class CategoryVisit(TimeStampModel):
    user: "User" = models.ForeignKey("bot.User", on_delete=models.CASCADE, related_name='category_visits')
    category: "Category" = models.ForeignKey("category.Category", on_delete=models.CASCADE,
                                             related_name='visits')

    def save(self, *args, **kwargs):
        # Get the current time
        now = timezone.now()
        # Define the time limit (1 hour ago)
        one_hour_ago = now - timedelta(hours=1)

        # Check if a visit already exists for this user and category within the last hour
        if not CategoryVisit.objects.filter(user=self.user, category=self.category,
                                            created_at__gte=one_hour_ago).exists():
            super().save(*args, **kwargs)


class ProductVisit(TimeStampModel):
    user: "User" = models.ForeignKey("bot.User", on_delete=models.CASCADE, related_name='product_visits')
    product: "Product" = models.ForeignKey("product.Product", on_delete=models.CASCADE, related_name='visits')

    def save(self, *args, **kwargs):
        # Get the current time
        now = timezone.now()
        # Define the time limit (1 hour ago)
        one_hour_ago = now - timedelta(hours=1)

        # Check if a visit already exists for this user and category within the last hour
        if not ProductVisit.objects.filter(user=self.user, product=self.product,
                                            created_at__gte=one_hour_ago).exists():
            super().save(*args, **kwargs)

    
    
    class Admin(admin.ModelAdmin):
        
        
        list_display = ["id","product","user"]
        
        list_filter = ["product","user"]
        
        search_fields = ["product__id"]