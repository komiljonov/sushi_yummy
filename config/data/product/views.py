from django.http import HttpRequest
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.product.models import Product
from data.product.serialisers import ProductCreateSerializer, ProductSerializer
from rest_framework.request import Request
from django.db.models import Q

# Create your views here.


class ProductListCreateAPIView(ListCreateAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer
    serializer_class_create = ProductCreateSerializer

    request: HttpRequest | Request

    def get_serializer_class(self):
        if self.request.method == "POST":
            return self.serializer_class_create
        return self.serializer_class

    def get_queryset(self):
        queryset = Product.objects.all()

        if self.request.query_params.get("notincategory") == "1":
            queryset = queryset.filter(
                Q(category=None)
                | Q(category_id=self.request.query_params.get("category"))
            )
            print(self.request.query_params.get("category"))

        if s := self.request.query_params.get("search"):
            queryset = queryset.filter(
                Q(name_uz__icontains=s) | Q(name_ru__icontains=s)
            )

        return queryset


class ProductRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer
    serializer_class_create = ProductCreateSerializer

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return self.serializer_class_create
        return self.serializer_class
