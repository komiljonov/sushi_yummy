from django.contrib.auth.models import User
from django.http import HttpRequest
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework.request import Request


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Add appropriate permissions as needed

    request: HttpRequest | Request

    def perform_create(self, serializer: UserSerializer):
        user: User = serializer.save()
        password = self.request.data.get("password")
        if password:
            user.set_password(password)
        user.is_staff = True
        user.save()

    def perform_update(self, serializer: UserSerializer):
        user: User = serializer.save()
        password = self.request.data.get("password")
        if password:
            user.set_password(password)
        user.is_staff = True
        user.save()
