import json
import os
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from data.cart.models import Cart
from utils.bot import Bot
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

            print(event)

            order = Cart.objects.filter(iiko_id=event.eventInfo.id).first()

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
                    "Sizning buyurtmangiz tayyorlanmoqda.\n\nTez orada yetkaziladi.",
                )
                
            print(f"Status: {event.eventInfo.order.status} {TOKEN}")

        return Response(data)
