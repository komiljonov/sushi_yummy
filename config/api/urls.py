from django.urls import path, include
from .views import StatisticsAPIView,XlsxAPIView
# from rest_framework.routers import DefaultRouter

# from data.users.views import UserViewSet


# router = DefaultRouter()
# router.register(r"users", UserViewSet)


urlpatterns = [
    path("auth/", include("api.auth.urls")),
    path("categories", include("data.category.urls")),
    path("products", include("data.product.urls")),
    path("files", include("data.file.urls")),
    path("orders", include("data.cart.urls")),
    path("payments", include("data.payment.urls")),

    path("filials", include("data.filial.urls")),
    path("referrals", include("data.referral.urls")),
    path("sync", include("data.sync.urls")),

    path("", include("data.admins.urls")),
    path("", include("data.promocode.urls")),
    path("", include("data.users.urls")),
    
    
    path("webhook", include("webhook.urls")),
    path("users", include("bot.urls")),
    path("delivery", include("data.taxi.urls")),
    
    
    path("statistics",StatisticsAPIView.as_view()),
    path("xlsx",XlsxAPIView.as_view()),
    
]
