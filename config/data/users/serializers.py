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

    class Meta:
        model = User

        fields = "__all__"

    def get_carts(self, obj: User):
        from data.cart.serializers import CartSerializer
        carts = obj.carts.exclude(Q(status="ORDERING") | Q(status="PENDING_PAYMENT"))

        return CartSerializer(carts, many=True).data
