from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.product.models import Product
from data.product.serialisers import ProductCreateSerializer, ProductSerializer

# Create your views here.


class ProductListCreateAPIView(ListCreateAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer
    serializer_class_create = ProductCreateSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return self.serializer_class
        return self.serializer_class_create


class ProductRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer
    serializer_class_create = ProductCreateSerializer

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return self.serializer_class_create
        return self.serializer_class
