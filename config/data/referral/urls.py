from django.urls import path
from .views import ReferralListAPIView, ReferralDetailAPIView

urlpatterns = [
    path("", ReferralListAPIView.as_view()),
    path("/<str:pk>", ReferralDetailAPIView.as_view()),
]
