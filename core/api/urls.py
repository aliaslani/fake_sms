# fake_sms/api/urls.py

from django.urls import path

from .views import (
    SendOTPAPIView,
    VerifyOTPAPIView,
)

urlpatterns = [
    path("send/", SendOTPAPIView.as_view()),
    path("verify/", VerifyOTPAPIView.as_view()),
]