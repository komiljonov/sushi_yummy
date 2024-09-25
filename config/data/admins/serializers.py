from data.admins.models import CustomUser
from rest_framework import serializers



class AdminSerializer(serializers.ModelSerializer):
    
    fullname = serializers.SerializerMethodField()
    
    
    class Meta:
        model = CustomUser
        fields = ["id", "username", "username", "filial", "role", "first_name", "last_name","fullname", "is_staff"]


    def get_fullname(self, obj:CustomUser):
        return obj.get_full_name()