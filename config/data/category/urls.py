from django.urls import path

from data.category.views import (
    CategoryListCreateAPIView,
    CategoryRetrieveUpdateDestroyAPIView,
)


urlpatterns = [
    path("", CategoryListCreateAPIView.as_view()),
    path("/<int:pk>", CategoryRetrieveUpdateDestroyAPIView.as_view()),
]
