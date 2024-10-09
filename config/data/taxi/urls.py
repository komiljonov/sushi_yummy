from django.urls import path
from .views import CalculateDeliveryPriceAPIView



urlpatterns = [
    path("/calculate", CalculateDeliveryPriceAPIView.as_view())
]