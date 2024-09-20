from django.contrib.auth.models import User
from rest_framework import serializers



class AdminSerializer(serializers.ModelSerializer):
    
    fullname = serializers.SerializerMethodField()
    
    
    class Meta:
        model = User
        fields = ["id", "username", "username", "first_name", "last_name","fullname", "is_staff"]


    def get_fullname(self, obj:User):
        return obj.get_full_name()