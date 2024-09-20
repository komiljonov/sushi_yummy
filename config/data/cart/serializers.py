from rest_framework import serializers

from bot.serializers import LocationSerializer
from data.cart.models import Cart
from data.cartitem.serializers import CartItemSerializer
from data.payment.serializers import PaymentSerializer
from django.db.models import Sum

from data.promocode.serializers import PromocodeSerializer
from data.users.serializers import UserSerializer


class CartSerializer(serializers.ModelSerializer):

    location = LocationSerializer()

    payment = PaymentSerializer()

    class Meta:
        model = Cart
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):

    # discount_price = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()
    # saving = serializers.SerializerMethodField()

    promocode = PromocodeSerializer()

    user = UserSerializer()

    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart

        fields = [
            "id",
            "order_id",
            "user",
            "products_count",
            "promocode",
            "order_time",
            "status",
            "price",
            "discount_price",
            "saving",
            "items",
            "comment",
        ]

    def get_products_count(self, obj: Cart):
        return obj.items.all().aggregate(total_count=Sum("count"))["total_count"]


    

    def __init__(self, *args, **kwargs):
        # Call the parent constructor

        # Fields you want to remove (for example, based on some condition)
        fields_to_remove = kwargs.pop("remove_fields", None)
        super(OrderSerializer, self).__init__(*args, **kwargs)

        if fields_to_remove:
            # Remove the fields from the serializer
            for field in fields_to_remove:
                self.fields.pop(field, None)
