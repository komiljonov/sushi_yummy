from datetime import datetime, timedelta
from io import BytesIO
from django.http import HttpRequest, HttpResponse
from rest_framework.views import APIView
from rest_framework.request import Request

from api.serializers import CartFilterSerializer
from api.xlsx import generate_excel_from_orders
from bot.models import User
from data.cart.models import Cart
from rest_framework.response import Response
from django.utils.timezone import make_aware
from django.db.models import Sum, Count
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from django.db.models import Subquery, OuterRef, Sum, Count, Q


from data.cart.serializers import OrderSerializer
from data.cartitem.models import CartItem
from data.product.models import Product


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
        users_yesterday = User.objects.filter(
            created_at__range=(yesterday_start, yesterday_end)
        )

        # Calculate user delta
        user_delta = users_today.count() - users_yesterday.count()

        # Orders excluding certain statuses for today and yesterday
        today_orders = Cart.objects.exclude(
            status__in=["ORDERING", "PENDING_PAYMENT"]
        ).filter(created_at__range=(today_start, today_end))

        yesterday_orders = Cart.objects.exclude(
            status__in=["ORDERING", "PENDING_PAYMENT"]
        ).filter(created_at__range=(yesterday_start, yesterday_end))

        # Calculate order delta
        orders_delta = today_orders.count() - yesterday_orders.count()

        # Revenue calculation for today and yesterday (since price is a custom property)
        today_revenue = sum(
            [order.discount_price for order in today_orders if order.price]
        )

        yesterday_revenue = sum(
            [order.price for order in yesterday_orders if order.price]
        )

        # Calculate revenue delta in percentage
        if yesterday_revenue != 0:
            revenue_delta_percent = (
                (today_revenue - yesterday_revenue) / yesterday_revenue
            ) * 100
        else:
            revenue_delta_percent = 100 if today_revenue > 0 else 0

        # Active users today (based on last update)
        active_users = User.objects.filter(last_update__range=(today_start, today_end))

        # distinct_products = CartItem.objects.filter(
        #     product__id=OuterRef("product__id")
        # ).values("product__id")

        # most_sold_products = (
        #     CartItem.objects.filter(product__id__in=Subquery(distinct_products))
        #     .values(
        #         "product__id", "product__name_uz", "product__price", "product__visits"
        #     )
        #     .annotate(total_count=Sum("count"), visit_count=Count("product__visits"))
        #     .order_by("-total_count")[:10]
        # )

        annotated_products = Product.objects.all()

        return Response(
            {
                "user_count": users.count(),
                "user_delta": user_delta,
                "orders_count": today_orders.count(),
                "orders_delta": orders_delta,
                "today_revenue": today_revenue,
                "revenue_delta_percent": round(
                    revenue_delta_percent, 2
                ),  # Rounded to 2 decimal places
                "active_users": active_users.count(),
                "active_users_delta": 43,
                "recent_orders": OrderSerializer(today_orders[:10], many=True).data,
                "most_products": [
                    {
                        "product__id": product.id,
                        "product__name_uz": product.name_uz,
                        "product__price": product.price,
                        "total_count": product.get_sale_count(),
                        "product__visits": product.visits.count(),
                    }
                    for product in annotated_products
                ],
            }
        )


class XlsxAPIView(APIView):

    def post(self, request: HttpRequest | Request, *args, **kwargs):
        serializer = CartFilterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            orders = serializer.filter_orders()

            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = (
                "attachment; filename=user_cart_statistics.xlsx"
            )

            # Save the workbook to the response
            generate_excel_from_orders(orders, response)

            return response

        return Response(serializer.errors, status=400)
