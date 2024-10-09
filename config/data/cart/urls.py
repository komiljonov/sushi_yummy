from django.urls import path
from .views import (
    OrderListAPIVIew,
    OrderRetrieveAPIView,
    OrderCallTaxiAPIView,
    OrderCreateAPIVIew,
)


urlpatterns = [
    path("", OrderListAPIVIew.as_view()),
    path("/create", OrderCreateAPIVIew.as_view()),
    path("/<str:pk>", OrderRetrieveAPIView.as_view()),
    path("/<str:pk>/call_taxi", OrderCallTaxiAPIView.as_view()),
]
