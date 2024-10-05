from django.urls import path
from .views import FilialsListAPIView, FilialsRetrieveAPIView

urlpatterns = [
    path("", FilialsListAPIView.as_view()),
    path("/<str:pk>", FilialsRetrieveAPIView.as_view())
]
