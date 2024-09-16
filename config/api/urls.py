from django.urls import path, include


urlpatterns = [
    path("auth/", include("api.auth.urls")),
    path("categories", include("data.category.urls")),
    path("products", include("data.product.urls")),
    path("files", include("data.file.urls")),
]
