from typing import TYPE_CHECKING
from django.db import models
from django.contrib import admin

from common.models import TimeStampModel

from django.utils import timezone
from django.db.models import Count, F

from django.db.models.functions import TruncDate
from datetime import timedelta
from data.analytics.models import CategoryVisit

if TYPE_CHECKING:
    from data.product.models import Product
    from data.filial.models import Filial


# Create your models here.


class Category(TimeStampModel):
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)

    filial: "Filial" = models.ForeignKey('filial.Filial', on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='categories')

    iiko_id = models.CharField(max_length=255)
    # name_us = models.CharField(max_length=255)

    parent: "Category" = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    children: "models.QuerySet[Category]"
    products: "models.QuerySet[Product]"
    visits: "models.QuerySet[CategoryVisit]"

    def __str__(self):
        return f"Category( {self.name_uz} )"

    class Meta:
        ordering = ["-created_at"]

    class Admin(admin.ModelAdmin):

        list_display = ["name_uz", "name_ru", "iiko_id", "filial", "parent"]

        search_fields = ["name_uz", "name_ru"]

        list_filter = ["filial"]

    @property
    def get_visit_analytics(self):
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)

        # Annotate visit counts for each day in the last 7 days
        visit_counts = (
            CategoryVisit.objects
            .filter(created_at__gte=last_7_days, category=self)
            .annotate(day=TruncDate('created_at'))  # Truncate time, keeping only the date
            .values('day')  # Group by the truncated date
            .annotate(count=Count('id'))  # Count visits
            .order_by('day')  # Order by date
        )

        # Prepare the analytics dictionary, defaulting to 0 for days without visits
        analytics = [
            {"date": (last_7_days + timedelta(days=i)).strftime('%Y-%m-%d'), "count": 0}
            for i in range(8)  # Last 7 days plus today
        ]

        # Update the counts in the analytics list
        for visit in visit_counts:
            for entry in analytics:
                if entry["date"] == visit['day'].strftime('%Y-%m-%d'):
                    entry["visits"] = visit['count']

        return analytics

    @property
    def get_visits_per_hour(self):
        # Get the current time and the time 7 days ago
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)

        # Annotate visit counts for each hour of the last 7 days
        visits_per_hour = (
            CategoryVisit.objects.filter(created_at__gte=seven_days_ago, category=self)
            .annotate(hour=F('created_at__hour'))  # Extract the hour from created_at
            .values('hour')  # Group by hour
            .annotate(visit_count=Count('id'))  # Count visits
            .order_by('hour')  # Order by hour
        )

        return visits_per_hour
