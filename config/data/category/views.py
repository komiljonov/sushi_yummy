from django.http import HttpRequest
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
)

from rest_framework.views import APIView

from data.category.models import Category
from data.category.serializers import (
    CategoryCreateSerializer,
    CategorySerializer,
    CategorySerializerWithStats,
)
from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from data.product.models import Product

# Create your views here.


class CategoryListCreateAPIView(ListCreateAPIView):

    queryset = Category.objects.filter(parent=None)

    serializer_class = CategorySerializer
    serializer_class_create = CategoryCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return self.serializer_class_create
        return self.serializer_class


class CategoryRetrieveAPIView(RetrieveAPIView):

    queryset = Category.objects.all()

    serializer_class = CategorySerializerWithStats


class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer


class CategoryProcutsAPIView(APIView):

    def get_category(self, pk: str):
        c = Category.objects.filter(id=pk).first()

        if c is None:
            raise NotFound("Kategoriya topilmadi.")

        return c

    def get(self, request: HttpRequest | Request, pk: str):

        category = self.get_category(pk)

        return Response({"data": category.products.values_list("id", flat=True)})

    def post(self, request: HttpRequest | Request, pk: str):

        category = self.get_category(pk)

        products_ids: list[str] = request.data.get("products")

        category.products.update(category=None)

        Product.objects.filter(id__in=products_ids).update(category=category)

        return Response({"data": category.products.values_list("id")})
