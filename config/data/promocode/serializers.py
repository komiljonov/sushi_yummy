from .models import Promocode
from rest_framework import serializers


class PromocodeSerializer(serializers.ModelSerializer):

    orders = serializers.SerializerMethodField()

    class Meta:
        model = Promocode
        fields = "__all__"

        required_fields = ["measurement"]

    def get_orders(self, obj: Promocode):
        from data.cart.serializers import OrderSerializer

        orders = obj.orders.all()

        serializer = OrderSerializer(orders, many=True, remove_fields=["promocode"])

        return serializer.data
