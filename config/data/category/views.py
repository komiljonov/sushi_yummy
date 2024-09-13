from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.category.models import Category
from data.category.serializers import CategoryCreateSerializer, CategorySerializer

# Create your views here.


class CategoryListCreateAPIView(ListCreateAPIView):

    queryset = Category.objects.filter(parent=None)

    serializer_class = CategorySerializer
    serializer_class_create = CategoryCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategoryCreateSerializer
        return CategorySerializer


class CategoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer
