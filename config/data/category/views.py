from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.category.models import Category
from data.category.serializers import CategoryCreateSerializer, CategorySerializer

# Create your views here.


class CategoryListAPIView(ListCreateAPIView):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer
    serializer_class_create = CategoryCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategoryCreateSerializer
        return CategorySerializer


class CategoryRetrieveAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer
