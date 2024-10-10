from rest_framework import serializers

from data.cart.models import Cart
from data.filial.models import Filial


class CartFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    delivery = serializers.ChoiceField(
        choices=["ALL", "DELIVERY", "PICKUP"], required=False, allow_null=True
    )
    filial = serializers.PrimaryKeyRelatedField(
        queryset=Filial.objects.all(), required=False
    )
    
    payment_type = serializers.ChoiceField(
        choices=["ALL", "CLICK", "PAYME", "CASH"],
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    def filter_orders(self):
        queryset = Cart.objects.all()

        # Filter by created_at range
        start_date = self.validated_data.get("start_date")
        end_date = self.validated_data.get("end_date")
        filial = self.validated_data.get("filial")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
        if filial:
            queryset = queryset.filter(filial=filial)
        elif start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        elif end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Filter by delivery method
        if (delivery := self.validated_data.get("delivery")) and delivery != "ALL":
            queryset = queryset.filter(delivery=self.validated_data["delivery"])

        # Filter by payment type
        if (
            payment_type := self.validated_data.get("payment_type")
        ) and payment_type != "ALL":
            queryset = queryset.filter(payment_type=self.validated_data["payment_type"])

        return queryset
