from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from data.taxi.models import Taxi


class TaxiSerializer(ModelSerializer):

    class Meta:
        model = Taxi

        fields = "__all__"




class CalculateDeliverySerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()