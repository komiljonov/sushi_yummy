from rest_framework import serializers

from bot.models import Location, User
from bot.serializers import LocationSerializer
from data.cart.models import Cart
from data.cartitem.serializers import CartItemSerializer
from data.filial.serializers import FilialSerializer
from data.payment.serializers import PaymentSerializer
from django.db.models import Sum

from data.product.models import Product
from data.promocode.serializers import PromocodeSerializer
from data.taxi.serializers import TaxiSerializer
from data.users.serializers import UserSerializer


class CartSerializer(serializers.ModelSerializer):
    location = LocationSerializer()

    payment = PaymentSerializer()

    taxi = TaxiSerializer()

    class Meta:
        model = Cart
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    payment = PaymentSerializer()

    promocode = PromocodeSerializer(
        remove_fields=[
            "orders",
        ]
    )

    filial = FilialSerializer()
    location = LocationSerializer()

    user = UserSerializer()

    taxi = TaxiSerializer()

    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart

        fields = [
            "id",
            "order_id",
            "user",
            "phone_number",
            "products_count",
            "promocode",
            "order_time",
            "time",
            "status",
            "price",
            "discount_price",
            "saving",
            "items",
            "comment",
            "payment",
            "filial",
            "location",
            "taxi",
        ]

    def get_products_count(self, obj: Cart):
        return obj.items.all().aggregate(total_count=Sum("count"))["total_count"]

    def __init__(self, *args, **kwargs):
        # Call the parent constructor

        # Fields you want to remove (for example, based on some condition)
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        super(OrderSerializer, self).__init__(*args, **kwargs)

        if fields_to_remove:
            # Remove the fields from the serializer
            for field in fields_to_remove:
                self.fields.pop(field, None)


class CreateOrderItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=True
    )
    quantity = serializers.IntegerField(required=True)


class CreateOrderSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    comment = serializers.CharField()
    phone = serializers.CharField()
    time = serializers.TimeField()

    delivery = serializers.ChoiceField(
        choices=[
            ("DELIVERY", "Yetkazib berish"),
            ("PICKUP", "Olib ketish"),
        ]
    )

    items = serializers.ListSerializer(child=CreateOrderItemSerializer())
