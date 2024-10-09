from rest_framework import serializers

from data.cart.models import Cart


class CartFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, null=True)
    end_date = serializers.DateField(required=False,null=True)
    delivery = serializers.ChoiceField(choices=["DELIVERY", "PICKUP"], required=False, null=True)
    payment_type = serializers.ChoiceField(
        choices=["CLICK", "PAYME", "CASH"], required=False, null=True
    )

    def filter_orders(self):
        queryset = Cart.objects.all()

        # Filter by created_at range
        if self.validated_data.get("start_date") and self.validated_data.get(
            "end_date"
        ):
            queryset = queryset.filter(
                created_at__range=[
                    self.validated_data["start_date"],
                    self.validated_data["end_date"],
                ]
            )
        elif self.validated_data.get("start_date"):
            queryset = queryset.filter(
                created_at__gte=self.validated_data["start_date"]
            )
        elif self.validated_data.get("end_date"):
            queryset = queryset.filter(created_at__lte=self.validated_data["end_date"])

        # Filter by delivery method
        if self.validated_data.get("delivery"):
            queryset = queryset.filter(delivery=self.validated_data["delivery"])

        # Filter by payment type
        if self.validated_data.get("payment_type"):
            queryset = queryset.filter(payment_type=self.validated_data["payment_type"])

        return queryset
