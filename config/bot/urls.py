from django.urls import path

from .views import SearchUsersAPIView


urlpatterns = [
    path("", SearchUsersAPIView.as_view()),
    path("/<str:search>", SearchUsersAPIView.as_view())
]
