from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromocodeViewSet,PromocodeXlsxAPIView

router = DefaultRouter()
router.register(r"promocodes", PromocodeViewSet)



urlpatterns = [
    path("/<str:pk>/xlsx", PromocodeXlsxAPIView.as_view()),
    path("", include(router.urls)),
]
