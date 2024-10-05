from django.http import HttpRequest
from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from data.cart.models import Cart
from data.cart.serializers import OrderSerializer
from django.db.models import Q
from rest_framework.request import Request
from rest_framework.exceptions import NotFound,bad_request

from data.taxi.serializers import TaxiSerializer
from utils.millenium import Millenium

# Create your views here.


class OrderListAPIVIew(ListAPIView):

    queryset = Cart.objects.exclude(
        Q(status="ORDERING") | Q(status="PENDING_PAYMENT")
    ).all()

    serializer_class = OrderSerializer


class OrderRetrieveAPIView(RetrieveAPIView):

    queryset = Cart.objects.all()

    serializer_class = OrderSerializer


class OrderCallTaxiAPIView(APIView):

    def get(self, request: HttpRequest | Request, pk: str):

        order = Cart.objects.filter(id=pk).first()

        if order is None:
            raise NotFound("Buyurtma topilmadi.")

        millenium = Millenium("3E8EA3F2-4776-4E1C-9A97-E4C13C5AEF1C")

        taxi = millenium.create_order(
            order.phone_number.replace("+",""), order.filial.location, order.location
        )
        
        if taxi is None:
            return bad_request(request, None)
        
        order.taxi = taxi
        order.save()
        
        return TaxiSerializer(taxi).data
