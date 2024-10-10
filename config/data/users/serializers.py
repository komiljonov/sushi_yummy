from rest_framework import serializers

from bot.models import User

from django.db.models import Q


class UserSerializer(serializers.ModelSerializer):

    has_order = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = "__all__"

    def get_has_order(self, obj: User):
        return obj.carts.exclude(
            Q(status="ORDERING") | Q(status="PENDING_PAYMENT")
        ).exists()


class RetrieveUserSerializer(serializers.ModelSerializer):

    carts = serializers.SerializerMethodField()

    current_order = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = "__all__"

    def get_carts(self, obj: User):
        from data.cart.serializers import OrderSerializer

        carts = obj.carts.exclude(Q(status="ORDERING") | Q(status="PENDING_PAYMENT"))

        return OrderSerializer(carts, many=True, remove_fields=["user"]).data

    def get_current_order(self, obj: User):
        from data.cart.serializers import OrderSerializer

        order = obj.carts.filter(
            status__in=["PENDING", "PENDING_KITCHEN", "PREPARING", "DELIVERING"],
            deleted_at=None,
        ).last()

        return OrderSerializer(
            order,
            remove_fields=["user"],
        ).data if order else None
