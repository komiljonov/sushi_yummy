from django.urls import path

from data.product.views import (
    ProductListCreateAPIView,
    ProductRetrieveUpdateDestroyAPIView,
)


urlpatterns = [
    path("", ProductListCreateAPIView.as_view()),
    path("/<int:pk>", ProductRetrieveUpdateDestroyAPIView.as_view()),
]
