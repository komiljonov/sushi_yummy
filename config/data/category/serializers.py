from rest_framework.serializers import ModelSerializer, SerializerMethodField

from data.category.models import Category
from data.product.serialisers import ProductSerializer


class SubCategory(ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class CategorySerializer(ModelSerializer):

    # products = ProductSerializer(many=True)

    products_count = SerializerMethodField()

    class Meta:
        model = Category

        fields = "__all__"

    def get_products_count(self, obj: Category):
        return obj.products.count()


class CategorySerializerWithStats(ModelSerializer):

    # products = ProductSerializer(many=True)
    products_count = SerializerMethodField()

    products = SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_products_count(self, obj: Category):
        return obj.products.count()

    def get_products(self, obj: Category):
        products = obj.products.all()

        return ProductSerializer(products, many=True, context=self.context).data


class CategoryCreateSerializer(ModelSerializer):

    class Meta:
        model = Category

        fields = "__all__"
