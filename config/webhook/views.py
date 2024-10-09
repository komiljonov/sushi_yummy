import json
import os
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from data.cart.models import Cart
from utils.bot import Bot
from utils.millenium import Millenium
from webhook.types import DeliveryOrderUpdate


TOKEN = os.getenv("TOKEN")

bot = Bot(TOKEN)


class IikoOrderUpdateAPIView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request: HttpRequest | Request):

        data = request.data

        print(data)

        events = [DeliveryOrderUpdate.from_dict(event) for event in data]

        for event in events:

            if event.eventType != "DeliveryOrderUpdate":
                continue

            order = Cart.objects.filter(iiko_id=event.eventInfo.id).first()

            print(order, event.eventInfo.id)

            if order is None:
                continue

            if event.eventInfo.order.status == "WaitCooking":

                order.status = "PENDING_KITCHEN"
                order.save()

                print("Send Message", TOKEN)

                bot.send_message(
                    order.user.chat_id, "Sizning buyurtmangiz tayyorlanishi kutilmoqda."
                )

            if event.eventInfo.order.status == "CookingStarted":

                order.status == "PREPARING"
                order.save()

                print("Send Message Started", TOKEN)

                bot.send_message(
                    order.user.chat_id,
                    f"Sizning buyurtmangiz tayyorlanmoqda.\n\nTez orada yetkaziladi.\n\n",
                )

                if order.delivery == "DELIVER":

                    millenium = Millenium("3E8EA3F2-4776-4E1C-9A97-E4C13C5AEF1C")

                    taxi = millenium.create_order(order)

                    order.taxi = taxi

                    order.save()

                    bot.send_message(
                        order.user.chat_id,
                        f"Sizning taxiingiz chaqirildi.\n\n"
                        f"Mashina raqami: {taxi.car_number}\n"
                        f"Mashina modeli: {taxi.car_model}\n"
                        f"Mashina rusmi: {taxi.car_mark}\n"
                        f"Mashina rangi: {taxi.car_color}\n"
                        f"Haydovchi telefon raqami: {taxi.driver_phone_number}"
                        f"Yetkazib berish narxi: {taxi.total_sum}",
                    )

            if event.eventInfo.order.status == "Cancelled":
                order.status = "CANCELLED"
                order.save()

                print("Send Message Cancellled", TOKEN)

                bot.send_message(
                    order.user.chat_id,
                    "Sizning buyurtmangiz bekor qilindi.",
                )

            print(f"Status: {event.eventInfo.order.status} {TOKEN}")

        return Response(data)
