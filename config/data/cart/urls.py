from django.urls import path
from .views import OrderListAPIVIew,OrderRetrieveAPIView


urlpatterns = [
    path("", OrderListAPIVIew.as_view()),
    path("/<str:pk>", OrderRetrieveAPIView.as_view())
]
