from django.shortcuts import render
from rest_framework.generics import ListAPIView,RetrieveAPIView

from data.product.models import Product
from data.product.serialisers import ProductSerializer



# Create your views here.




class ProductListAPIView(ListAPIView):
    
    queryset = Product.objects.all()
    
    serializer_class = ProductSerializer
    
    
class ProductRetrieveAPIView(RetrieveAPIView):
    
    queryset = Product.objects.all()
    
    serializer_class = ProductSerializer