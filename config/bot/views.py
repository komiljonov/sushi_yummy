from django.shortcuts import render
from rest_framework.generics import ListAPIView

from bot.models import User
from data.users.serializers import UserSerializer
# Create your views here.




class SearchUsersAPIView(ListAPIView):
    
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        if q := self.kwargs.get('search'):
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(number__icontains=q)
            )
        
        return queryset