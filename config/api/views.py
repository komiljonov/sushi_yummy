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
from openpyxl.styles import Alignment


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

    def post(self, request, *args, **kwargs):
        # Get all users with related carts
        users = User.objects.prefetch_related("carts").all()

        # Generate the XLSX file
        wb = self.generate_user_cart_statistics(users)

        # Prepare the response with the XLSX file
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            "attachment; filename=user_cart_statistics.xlsx"
        )

        # Save the workbook to the response
        wb.save(response)

        return response

    def generate_user_cart_statistics(self, users: list[User]):
        # Create a workbook and select the active sheet
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "User Cart Statistics"

        # Add headers (customize based on your uploaded file)
        headers = [
            "Foydalanuvchi",
            "Foydalanuvchi ma'lumotlari",
            "Birinchi start bosgan vaqti",
            "Buyurtma idsi",
            "Buyurtma holati",
            "TO'liq narxi",
            "Chegirma",
            "Ohirgi narx",
            "Yetkazish turi",
            "Joylashuv",
            "To'lov holati",
        ]
        sheet.append(headers)

        row_num = 2  # Starting row (after headers)

        for idx, user in enumerate(users, start=1):
            # Write user header
            sheet[f"A{row_num}"] = f"{idx}. User"
            sheet[f"B{row_num}"] = (
                f"{user.name or 'No Name'} - {user.number or 'No Number'}"
            )
            sheet[f"B{row_num}"].alignment = Alignment(horizontal="left")
            sheet[f"C{row_num}"] = user.created_at.strftime("%d/%m/%Y, %H:%M:%S")

            row_num += 1  # Move to the next row

            # Write cart data for the user
            for cart in user.carts.all():
                sheet[f"D{row_num}"] = cart.order_id  # Order ID
                sheet[f"E{row_num}"] = cart.status  # Order Status
                sheet[f"F{row_num}"] = cart.price  # Total Price
                sheet[f"G{row_num}"] = cart.saving  # Discount
                sheet[f"H{row_num}"] = cart.discount_price  # Final Price
                sheet[f"I{row_num}"] = cart.delivery  # Delivery Method
                sheet[f"J{row_num}"] = (
                    cart.location.name if cart.location else "N/A"
                )  # Location
                sheet[f"K{row_num}"] = (
                    cart.payment.status if cart.payment else "Unpaid"
                )  # Payment Status

                # Align all data cells
                for col in range(4, 12):  # From columns D to K
                    sheet[f"{get_column_letter(col)}{row_num}"].alignment = Alignment(
                        horizontal="left"
                    )

                row_num += 1

            # Add an empty row after each user's data
            row_num += 1

        # Adjust column width for readability
        for col in range(1, sheet.max_column + 1):
            column_letter = get_column_letter(col)
            sheet.column_dimensions[column_letter].width = (
                25  # Set width for each column
            )

        return wb
