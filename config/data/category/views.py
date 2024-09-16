from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
)

from data.category.models import Category
from data.category.serializers import (
    CategoryCreateSerializer,
    CategorySerializer,
    CategorySerializerWithStats,
)

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
