from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from data.promocode.models import Promocode
from .serializers import PromocodeSerializer

# Create your views here.


class PromocodeViewSet(viewsets.ModelViewSet):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = [IsAuthenticated]  # Add appropriate permissions as needed
