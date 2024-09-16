from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from .models import File
from .serializers import FileSerializer
from django.http import HttpRequest


# Create your views here.


class FileListAPIView(ListAPIView):
    queryset = File.objects.all()

    serializer_class = FileSerializer


class FileUploadView(APIView):
    def post(self, request: HttpRequest | Request, *args, **kwargs):
        serializer = FileSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            file = serializer.save()

            # info = FileInfoSerializer(file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileInfoView(RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    lookup_field = "pk"
