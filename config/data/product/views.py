from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.product.models import Product
from data.product.serialisers import ProductSerializer


# Create your views here.


class ProductListCreateAPIView(ListCreateAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer


class ProductRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer
