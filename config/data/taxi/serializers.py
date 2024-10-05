from rest_framework.serializers import ModelSerializer

from data.taxi.models import Taxi


class TaxiSerializer(ModelSerializer):

    class Meta:
        model = Taxi

        fields = "__all__"
