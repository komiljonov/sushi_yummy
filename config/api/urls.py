from django.urls import path, include

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

    path("", include("data.admins.urls")),
    path("", include("data.promocode.urls")),
    path("", include("data.users.urls")),
    # path("", include(router.urls)),
]
