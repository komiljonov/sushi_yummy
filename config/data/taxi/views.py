from django.http import HttpRequest
from rest_framework.request import Request

from bot.models import Location
from data.filial.models import Filial
from data.taxi.serializers import CalculateDeliverySerializer
from utils.geocoder import reverse_geocode
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.millenium import Millenium


millenium = Millenium("3E8EA3F2-4776-4E1C-9A97-E4C13C5AEF1C")


class CalculateDeliveryPriceAPIView(APIView):

    def post(self, request: HttpRequest | Request):

        serializer = CalculateDeliverySerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        loc = Location(
            latitude=serializer.get("latitude"),
            longitude=serializer.get("longitude"),
        )

        filial = Filial.get_nearest_filial(loc)

        cost = millenium.calc_order_cost(filial.location, loc)

        address = reverse_geocode(loc.latitude, loc.longitude)

        return Response({"address": address, "cost": cost["info"][-1]["sum"]})
