from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.request import Request


class IikoOrderUpdateAPIView(APIView):

    def post(self, request: HttpRequest | Request):

        print("Headers", request.headers)

        data = request.data
        print("Data", data)

        body = request.body
        print("Body", body)
