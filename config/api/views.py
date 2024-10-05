from datetime import datetime, timedelta
from io import BytesIO
from django.http import HttpRequest, HttpResponse
from rest_framework.views import APIView
from rest_framework.request import Request

from bot.models import User
from data.cart.models import Cart
from rest_framework.response import Response
from django.utils.timezone import make_aware
from django.db.models import Sum
import openpyxl
from openpyxl.utils import get_column_letter



from data.cart.serializers import OrderSerializer


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
        today_revenue = sum([order.price for order in today_orders if order.price])
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
            }
        )

class XlsxAPIView(APIView):

    def post(self, request: HttpRequest | Request):

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Cart Orders"

        # Define headers based on the structure of the provided Excel file
        headers = [
            "Oy.sana.kun (start bosilgan data)", "Ism", "Tel. nomer", 
            "Zakaz (summa)", "Usp ID", "Usp (summa)", 
            "Otmen ID", "Otmen (summa)", "Data Otmen (zakaz)"
        ]
        
        # Append headers to the worksheet
        ws.append(headers)

        # Fetch cart data (replace this with your actual database query)
        carts = Cart.objects.all()  # Assuming this returns all Cart instances
        
        # Loop through the cart entries and add rows to the sheet
        for cart in carts:
            row = [
                cart.created_at.strftime("%Y-%m-%d"),  # Assuming this is the order creation date
                cart.user.tg_name if cart.user else "Unknown",  # User name
                cart.phone_number,  # Phone number
                cart.price,  # Order price
                cart.order_id,  # Order ID
                cart.discount_price,  # Discounted price (Usp summa)
                None,  # Assuming Otmen ID is null in this case
                None,  # Assuming Otmen summa is null in this case
                None   # Assuming Data Otmen is null in this case
            ]
            
            # Append each row to the worksheet
            ws.append(row)

        # Adjust column width
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 20
        
        # Save the workbook to a BytesIO stream instead of a file
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # Create the response with the appropriate headers
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=cart_orders.xlsx'

        return response