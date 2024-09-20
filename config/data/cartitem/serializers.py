from rest_framework import serializers

from data.cartitem.models import CartItem
from data.product.serialisers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):

    total_price = serializers.SerializerMethodField()
    
    product = ProductSerializer()

    class Meta:
        model = CartItem

        fields = ["id", "product", "count", "price", "total_price"]

    def get_total_price(self, obj: CartItem):
        return obj.count * obj.price
