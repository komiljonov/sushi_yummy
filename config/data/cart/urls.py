from django.urls import path
from .views import OrderListAPIVIew,OrderRetrieveAPIView,OrderCallTaxiAPIView


urlpatterns = [
    path("", OrderListAPIVIew.as_view()),
    path("/<str:pk>", OrderRetrieveAPIView.as_view()),
    path("/<str:pk>/call_taxi", OrderCallTaxiAPIView.as_view()),
    
]
