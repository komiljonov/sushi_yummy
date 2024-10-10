from .models import Promocode
from rest_framework import serializers


class PromocodeSerializer(serializers.ModelSerializer):

    orders = serializers.SerializerMethodField()

    total_savings = serializers.SerializerMethodField()
    total_sold = serializers.SerializerMethodField()

    class Meta:
        model = Promocode
        fields = "__all__"

        required_fields = ["measurement"]

    def get_orders(self, obj: Promocode):
        from data.cart.serializers import OrderSerializer

        orders = obj.orders.all()

        serializer = OrderSerializer(orders, many=True, remove_fields=["promocode"])

        return serializer.data

    def __init__(self, *args, **kwargs):
        # Call the parent constructor

        # Fields you want to remove (for example, based on some condition)
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        super(PromocodeSerializer, self).__init__(*args, **kwargs)

        if fields_to_remove:
            # Remove the fields from the serializer
            for field in fields_to_remove:
                self.fields.pop(field, None)

    def get_total_savings(self, obj: Promocode):

        return sum([order.saving for order in obj.orders.all()])

    def get_total_sold(self, obj: Promocode):

        return sum([order.price for order in obj.orders.all()])
