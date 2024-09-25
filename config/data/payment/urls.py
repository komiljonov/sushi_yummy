from django.urls import path

from data.payment.views import PaymentListAPIView

urlpatterns = [
    path("", PaymentListAPIView.as_view())
]