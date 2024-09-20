from bot.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer,RetrieveUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Add appropriate permissions as needed

    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer  # Serializer for listing users
        if self.action == 'retrieve':
            return RetrieveUserSerializer  # Serializer for retrieving detailed user info
        return super().get_serializer_class()  # Default behavior