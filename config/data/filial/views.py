from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView

from data.filial.models import Filial
from data.filial.serializers import FilialSerializer


# Create your views here.


class FilialsListAPIView(ListCreateAPIView):
    queryset = Filial.objects.all()

    serializer_class = FilialSerializer


class FilialsRetrieveAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer

