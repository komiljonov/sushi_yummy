from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromocodeViewSet

router = DefaultRouter()
router.register(r"promocodes", PromocodeViewSet)



urlpatterns = [
    path("", include(router.urls)),
]
