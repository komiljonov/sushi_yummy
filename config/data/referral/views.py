from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.referral.models import Referral
from data.referral.serializers import ReferralSerializer


# Create your views here.


class ReferralListAPIView(ListCreateAPIView):
    queryset = Referral.objects.all()

    serializer_class = ReferralSerializer


class ReferralDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Referral.objects.all()

    serializer_class = ReferralSerializer
