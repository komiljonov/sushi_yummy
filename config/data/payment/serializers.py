from rest_framework import serializers


from data.payment.models import Payment
from data.users.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):

    order = serializers.SerializerMethodField()
    user = UserSerializer()
    
    class Meta:
        model = Payment
        
        fields = "__all__"

    def get_order(self, obj: Payment):
        from data.cart.serializers import OrderSerializer
        try:
            if obj.order:
                return OrderSerializer(obj.order, remove_fields=["payment"]).data
        except Exception as e:
            print(e)