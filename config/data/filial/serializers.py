from rest_framework import serializers
from bot.models import Location
from bot.serializers import LocationSerializer
from data.filial.models import Filial

class FilialSerializer(serializers.ModelSerializer):
    loc_latitude = serializers.FloatField(write_only=True, required=True)
    loc_longitude = serializers.FloatField(write_only=True, required=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Filial
        fields = [
            "id",
            "name_uz",
            "name_ru",
            "loc_latitude",
            "loc_longitude",
            "location"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:  # If an instance exists, it's an update operation
            self.fields['loc_latitude'].required = False
            self.fields['loc_longitude'].required = False

    def create(self, validated_data: dict):
        # Extract location-related data
        loc_latitude = validated_data.pop('loc_latitude')
        loc_longitude = validated_data.pop('loc_longitude')

        # Create a new location
        new_location = Location.objects.create(
            name=validated_data.get("name_uz"),
            address=validated_data.get("name_uz"),
            latitude=loc_latitude,
            longitude=loc_longitude,
            special=True,
            used=True
        )

        # Create the Filial with the new location
        filial = Filial.objects.create(
            **validated_data,
            location=new_location
        )

        return filial

    def update(self, instance, validated_data: dict):
        # Get the existing location of the instance
        location = instance.location

        # Check if loc_latitude and loc_longitude are provided
        loc_latitude = validated_data.pop('loc_latitude', None)
        loc_longitude = validated_data.pop('loc_longitude', None)

        if loc_latitude is not None and loc_longitude is not None:
            # Update the location if both latitude and longitude are provided
            location.latitude = loc_latitude
            location.longitude = loc_longitude
            location.save()

        # Update other Filial fields
        instance.name_uz = validated_data.get('name_uz', instance.name_uz)
        instance.name_ru = validated_data.get('name_ru', instance.name_ru)
        instance.save()

        return instance
