from datetime import datetime, timedelta
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.request import Request

from bot.models import User
from data.cart.models import Cart
from rest_framework.response import Response
from django.utils.timezone import make_aware
from django.db.models import Sum

class StatisticsAPIView(APIView):

    def get(self, request: HttpRequest | Request):
        
        # Get all users
        users = User.objects.all()

        # Get today's and yesterday's date
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Make the datetime objects timezone-aware
        today_start = make_aware(datetime.combine(today, datetime.min.time()))
        today_end = make_aware(datetime.combine(today, datetime.max.time()))
        yesterday_start = make_aware(datetime.combine(yesterday, datetime.min.time()))
        yesterday_end = make_aware(datetime.combine(yesterday, datetime.max.time()))

        # Users created today and yesterday
        users_today = User.objects.filter(created_at__range=(today_start, today_end))
        users_yesterday = User.objects.filter(created_at__range=(yesterday_start, yesterday_end))

        # Calculate user delta
        user_delta = users_today.count() - users_yesterday.count()

        # Orders excluding certain statuses for today and yesterday
        today_orders = Cart.objects.exclude(status__in=["ORDERING", "PENDING_PAYMENT"]).filter(
            created_at__range=(today_start, today_end)
        )
        yesterday_orders = Cart.objects.exclude(status__in=["ORDERING", "PENDING_PAYMENT"]).filter(
            created_at__range=(yesterday_start, yesterday_end)
        )

        # Calculate order delta
        orders_delta = today_orders.count() - yesterday_orders.count()

        # Revenue calculation for today and yesterday (since price is a custom property)
        today_revenue = sum([order.price for order in today_orders])
        yesterday_revenue = sum([order.price for order in yesterday_orders])

        # Calculate revenue delta
        revenue_delta = today_revenue - yesterday_revenue

        # Active users today (based on last update)
        active_users = User.objects.filter(last_update__range=(today_start, today_end))

        return Response({
            "user_count": users.count(),
            "user_delta": user_delta,
            "orders_count": today_orders.count(),
            "orders_delta": orders_delta,
            "today_revenue": today_revenue,
            "revenue_delta": revenue_delta,
            "active_users": active_users.count(),
            "active_users_delta": 43,  # Placeholder, if you want similar logic for active_users
        })