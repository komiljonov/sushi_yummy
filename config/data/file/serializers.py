from rest_framework.serializers import ModelSerializer, SerializerMethodField

from data.file.models import File
from django.http import HttpRequest


class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "file", "filename", "created_at", "updated_at"]
        
        read_only_fields = [
            "id",
            "filename",
            "created_at",
            "updated_at"
        ]

    def create(self, validated_data: dict):
        file_instance = File.objects.create(
            file=validated_data.get("file"), filename=validated_data.get("file").name
        )
        return file_instance
