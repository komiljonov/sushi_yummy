from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import HttpRequest, Request
from rest_framework import status
from django.contrib.auth.models import User

from api.auth.serializers import ChangePasswordSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data
        access_token = data.get("access")
        refresh_token = data.get("refresh")

        # Set the tokens in cookies
        response.set_cookie(
            "access_token", access_token, httponly=True, secure=True, samesite="Lax"
        )
        response.set_cookie(
            "refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax"
        )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data
        access_token = data.get("access")

        # Set the new access token in cookies
        response.set_cookie(
            "access_token", access_token, httponly=True, secure=True, samesite="Lax"
        )

        return response


class Me(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request: Request | HttpRequest, *args, **kwargs):
        user: User = request.user
        print(type(user))

        user_data = {
            "name": user.get_full_name(),  # Assuming the user's name is stored in get_full_name()
            "status": "active" if user.is_active else "inactive",
        }
        return Response(user_data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request | HttpRequest, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password updated successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
