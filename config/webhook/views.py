from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.permissions import AllowAny


class IikoOrderUpdateAPIView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [AllowAny]  # Allow any user to access this view

    def post(self, request: HttpRequest | Request):
        print("Headers", request.headers)

        data = request.data
        print("Data", data)

        body = request.body
        print("Body", body)
