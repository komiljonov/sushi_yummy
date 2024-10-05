from rest_framework import serializers

from bot.models import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location

        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "address"
        ]
