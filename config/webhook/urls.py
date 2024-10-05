from django.urls import path

from .views import IikoOrderUpdateAPIView


urlpatterns = [
    path("iiko",IikoOrderUpdateAPIView.as_view())
]