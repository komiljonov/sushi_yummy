from django.http import HttpRequest
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from data.cart.models import Cart
from data.cart.serializers import CreateOrderSerializer, OrderSerializer
from django.db.models import Q
from rest_framework.request import Request
from rest_framework.exceptions import NotFound, bad_request
from rest_framework.generics import CreateAPIView

from data.taxi.serializers import TaxiSerializer
from utils.millenium import Millenium
from rest_framework.response import Response
from rest_framework import status

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

        taxi = millenium.create_order(order)

        if taxi is None:
            return bad_request(request, None)

        order.taxi = taxi
        order.save()

        return Response(TaxiSerializer(taxi).data)


class OrderCreateAPIVIew(CreateAPIView):
    
    serializer_class = CreateOrderSerializer

    request: HttpRequest | Request

    def perform_create(self, serializer):
        # Create the order using the validated data
        self.order = serializer.save()

    def post(self, request: HttpRequest | Request, *args, **kwargs):
        # Use CreateOrderSerializer for input validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Perform the creation logic and save the order
        self.perform_create(serializer)

        # Use OrderResponseSerializer to format the response
        response_serializer = OrderSerializer(self.order)

        # Return the response with the newly created data
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
