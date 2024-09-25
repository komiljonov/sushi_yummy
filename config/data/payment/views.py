from django.shortcuts import render
from rest_framework.generics import  ListAPIView

from data.payment.models import Payment
from data.payment.serializers import PaymentSerializer


# Create your views here.




class PaymentListAPIView(ListAPIView):

    queryset = Payment.objects.all()

    serializer_class = PaymentSerializer