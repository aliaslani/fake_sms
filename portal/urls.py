# fake_sms/portal/urls.py

from django.urls import path

from .views import otp_lookup

urlpatterns = [
    path("", otp_lookup, name="otp_lookup"),
]