from rest_framework import serializers

from bot.models import Location, User
from bot.serializers import LocationSerializer
from data.cart.models import Cart
from data.cartitem.serializers import CartItemSerializer
from data.filial.models import Filial
from data.filial.serializers import FilialSerializer
from data.payment.serializers import PaymentSerializer
from django.db.models import Sum

from data.product.models import Product
from data.promocode.models import Promocode
from data.promocode.serializers import PromocodeSerializer
from data.taxi.serializers import TaxiSerializer
from data.users.serializers import UserSerializer

from django.utils.timezone import now

from utils.geocoder import reverse_geocode


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


class CreateOrderLocationSerializer(serializers.Serializer):

    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class CreateOrderSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    comment = serializers.CharField()
    phone = serializers.CharField()
    time = serializers.TimeField()

    promocode = serializers.PrimaryKeyRelatedField(
        queryset=Promocode.objects.all(), required=False
    )

    location = CreateOrderLocationSerializer(required=False)

    filial = serializers.PrimaryKeyRelatedField(
        queryset=Filial.objects.all(), required=False
    )

    delivery = serializers.ChoiceField(
        choices=[
            ("DELIVERY", "Yetkazib berish"),
            ("PICKUP", "Olib ketish"),
        ]
    )

    items = serializers.ListSerializer(
        child=CreateOrderItemSerializer(), allow_empty=False
    )

    def validate(self, data):
        delivery_type = data.get("delivery")

        if delivery_type == "DELIVERY" and not data.get("location"):
            raise serializers.ValidationError(
                {"location": "Location is required for delivery orders."}
            )

        if delivery_type == "PICKUP" and not data.get("filial"):
            raise serializers.ValidationError(
                {"filial": "Filial is required for pickup orders."}
            )

        return data

    def create(self, validated_data: dict):

        location = (
            [
                validated_data.get("location").get("latitude"),
                validated_data.get("location").get("longitude"),
            ]
            if validated_data.get("location")
            else None
        )

        new_cart = Cart.objects.create(
            user=validated_data.get("user"),
            phone=validated_data.get("phone"),
            promocode=validated_data.get("promocode"),
            delivery=validated_data.get("delivery"),
            time=validated_data.get("time"),
            filial=validated_data.get("filial"),
            location=(
                Location.objects.create(
                    user=validated_data.get("user"),
                    latitude=location[0],
                    longitude=location[1],
                    address=reverse_geocode(*location),
                )
                if location
                else None
            ),
            order_time=now(),
        )

        for item in validated_data.get("items"):
            product: "Product" = item.get("product")
            new_cart.items.create(
                product=product, price=product.price, count=item.get("quantity")
            )
