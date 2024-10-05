from rest_framework.serializers import ModelSerializer, SerializerMethodField

from data.category.models import Category
from data.filial.serializers import FilialSerializer
from data.product.serialisers import ProductSerializer
from datetime import date


class SubCategory(ModelSerializer):

    # filial = FilialSerializer()

    class Meta:
        model = Category
        fields = "__all__"


class CategorySerializer(ModelSerializer):

    # products = ProductSerializer(many=True)

    children_count = SerializerMethodField()

    products_count = SerializerMethodField()
    today_visits = SerializerMethodField()
    
    children = SerializerMethodField()

    class Meta:
        model = Category

        fields = "__all__"

    def get_products_count(self, obj: Category):
        return obj.products.count()

    def get_today_visits(self, obj: Category):
        return obj.visits.filter(created_at__date=date.today()).count()

    def get_children_count(self, obj: Category):

        return obj.children.count()
    
    def get_children(self, obj: Category):
        
        return CategorySerializer(obj.children.all(),many=True).data


class CategorySerializerWithStats(ModelSerializer):

    # products = ProductSerializer(many=True)
    products_count = SerializerMethodField()

    visits = SerializerMethodField()
    average_visit_time = SerializerMethodField()

    products = SerializerMethodField()

    children = CategorySerializer(many=True)

    class Meta:
        model = Category
        fields = "__all__"

    def get_products_count(self, obj: Category):
        return obj.products.count()

    def get_products(self, obj: Category):
        products = obj.products.all()

        return ProductSerializer(products, many=True, context=self.context).data

    def get_visits(self, obj: Category):
        return obj.get_visit_analytics

    def get_average_visit_time(self, obj: Category):
        return obj.get_visits_per_hour


class CategoryCreateSerializer(ModelSerializer):

    class Meta:
        model = Category

        fields = "__all__"
