from django.http import HttpRequest, HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from api.xlsx import generate_excel_from_orders
from data.promocode.models import Promocode
from .serializers import PromocodeSerializer
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action


# Create your views here.


class PromocodeViewSet(viewsets.ModelViewSet):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    permission_classes = [IsAuthenticated]  # Add appropriate permissions as needed
    
    
    @action(detail=True, methods=['get'], url_path='xlsx')
    def get(self, request: HttpRequest | Request, pk: str):

        # promocode = Promocode.objects.filter(id=pk).first()

        # if promocode is None:
            # raise NotFound("Promokod topilmadi.")
        
        promocode: Promocode = self.get_object()

        orders = promocode.orders.all()

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f"attachment; filename={promocode.name}_statistics.xlsx"
        )

        generate_excel_from_orders(orders, response)

        return response

