from django.contrib.auth import update_session_auth_hash
from rest_framework.serializers import Serializer, CharField, ValidationError
from django.contrib.auth.models import User
from django.http import HttpRequest


class ChangePasswordSerializer(Serializer):
    old_password = CharField(write_only=True)
    new_password = CharField(write_only=True)

    def validate_old_password(self, value):
        request: "HttpRequest" = self.context["request"]
        user: User = request.user
        if not user.check_password(value):
            raise ValidationError("Old password is not correct.")
        return value

    def validate(self, data):
        return data

    def save(self):
        request: HttpRequest = self.context["request"]
        user: User = request.user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(self.context["request"], user)
