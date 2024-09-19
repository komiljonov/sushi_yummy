from .models import Promocode
from rest_framework import serializers


class PromocodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Promocode
        fields = "__all__"

        required_fields = ["measurement"]
