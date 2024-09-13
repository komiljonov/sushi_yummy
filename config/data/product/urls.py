from django.urls import path

from data.product.views import ProductListAPIView, ProductRetrieveAPIView


urlpatterns = [
    path("", ProductListAPIView.as_view()),
    path("<int:pk>", ProductRetrieveAPIView.as_view()),
]
