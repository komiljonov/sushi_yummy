from rest_framework.serializers import ModelSerializer

from data.category.models import Category
from data.product.serialisers import ProductSerializer


class SubCategory(ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class CategorySerializer(ModelSerializer):

    subcategories = SubCategory(many=True)

    products = ProductSerializer(many=True)

    class Meta:
        model = Category

        fields = "__all__"
