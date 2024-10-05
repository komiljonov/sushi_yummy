import base64

from rest_framework import serializers

from data.referral.models import Referral
from data.users.serializers import UserSerializer
import os


class ReferralSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    users_count = serializers.SerializerMethodField()

    link = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        model = Referral

    def get_users_count(self, obj: Referral):
        return obj.users.count()

    def get_link(self, obj: Referral):
        return os.getenv("BOT_USER", "").format(start=base64.b64encode(f"{obj.id}".encode()).decode())
