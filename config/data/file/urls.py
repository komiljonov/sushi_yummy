from django.urls import path
from .views import FileUploadView, FileInfoView,FileListAPIView


urlpatterns = [
    path("", FileListAPIView.as_view(), name="files"),
    path("/upload", FileUploadView.as_view(), name="file-upload"),
    path("/<int:pk>/", FileInfoView.as_view(), name="file-info"),
]
