# fake_sms/portal/views.py

from django.shortcuts import render

from core.services.otp_store import OTPStoreService


def otp_lookup(request):

    mobile = request.GET.get("mobile")

    otp_data = None

    if mobile:
        otp_data = OTPStoreService.get(mobile)

    return render(
        request,
        "portal/index.html",
        {
            "mobile": mobile,
            "otp_data": otp_data,
        }
    )