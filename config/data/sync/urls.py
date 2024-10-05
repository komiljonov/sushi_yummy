from django.urls import path
from .views import SyncAPIView



urlpatterns = [
    path("", SyncAPIView.as_view())
]