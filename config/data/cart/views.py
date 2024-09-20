from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView

from data.cart.models import Cart
from data.cart.serializers import OrderSerializer
from django.db.models import Q

# Create your views here.


class OrderListAPIVIew(ListAPIView):

    queryset = Cart.objects.exclude(Q(status="ORDERING") | Q(status="PENDING_PAYMENT")).all()

    serializer_class = OrderSerializer


class OrderRetrieveAPIView(RetrieveAPIView):

    queryset = Cart.objects.all()

    serializer_class = OrderSerializer
