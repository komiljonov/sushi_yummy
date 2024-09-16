from django.urls import path

# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    Me,
)


urlpatterns = [
    path("token", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me", Me.as_view()),
    path("change_password", ChangePasswordView.as_view()),
]
