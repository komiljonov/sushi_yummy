from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
)

from data.category.models import Category

# from data.category.serializers import CategorySerializer
from data.file.models import File
from data.file.serializers import FileSerializer
from data.product.models import Product


class ProductSerializer(ModelSerializer):
    # category = CategorySerializer()

    todays_sells = SerializerMethodField()
    sale_count = SerializerMethodField()

    image = FileSerializer()

    class Meta:
        model = Product

        fields = "__all__"

    def get_todays_sells(self, obj: Product):
        # TODO: Implement today's total sells
        return 0

    def get_sale_count(self, obj: Product):
        return 5
        return obj.cart_items.filter(cart__status__in=[
            "PENDING_PAYMENT",
            "PENDING",
            "PENDING_KITCHEN",
            "PREPARING",
            "DELIVERING",
            "DONE",
        ]).count()


class ProductCreateSerializer(ModelSerializer):
    category = PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    image = PrimaryKeyRelatedField(queryset=File.objects.all(), required=True)

    class Meta:
        model = Product

        fields = "__all__"
