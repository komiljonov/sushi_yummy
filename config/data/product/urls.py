from django.urls import path

from data.product.views import (
    ProductListCreateAPIView,
    ProductRetrieveUpdateDestroyAPIView,
)


urlpatterns = [
    path("", ProductListCreateAPIView.as_view()),
    path("/<str:pk>", ProductRetrieveUpdateDestroyAPIView.as_view()),
]
