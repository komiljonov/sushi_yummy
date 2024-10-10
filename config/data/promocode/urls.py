from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromocodeViewSet,PromocodeXlsxAPIView

router = DefaultRouter()
router.register(r"promocodes", PromocodeViewSet)



urlpatterns = [
    path("", include(router.urls)),
    path("/<str:pk>/xlsx", PromocodeXlsxAPIView.as_view())
]
