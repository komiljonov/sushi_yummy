from django.urls import path

from data.category.views import (
    CategoryListCreateAPIView,
    CategoryRetrieveAPIView,
    CategoryRetrieveUpdateDestroyAPIView,
    CategoryProcutsAPIView
)

urlpatterns = [
    path("", CategoryListCreateAPIView.as_view()),
    path("/<str:pk>", CategoryRetrieveUpdateDestroyAPIView.as_view()),
    path("/<str:pk>/stats", CategoryRetrieveAPIView.as_view()),
    path("/<str:pk>/products", CategoryProcutsAPIView.as_view()),
]
