from django.urls import path, include


urlpatterns = [
    path("auth/", include("api.auth.urls")),
    path("category", include("data.category.urls")),
    path("product", include("data.product.urls")),
]
