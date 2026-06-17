from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle


def _get_throttle_rates():
    rest_framework = getattr(settings, "REST_FRAMEWORK", {})
    return rest_framework.get("DEFAULT_THROTTLE_RATES", {})


class OTPIPThrottle(SimpleRateThrottle):
    def get_rate(self):
        return _get_throttle_rates().get(self.scope)

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)

        if not ident:
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class OTPMobileThrottle(SimpleRateThrottle):
    mobile_field = "mobile"

    def get_rate(self):
        return _get_throttle_rates().get(self.scope)

    def get_cache_key(self, request, view):
        mobile = request.data.get(self.mobile_field)

        if mobile is None:
            return None

        normalized = "".join(ch for ch in str(mobile) if ch.isdigit())

        if not normalized:
            normalized = str(mobile).strip()

        if not normalized:
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": normalized,
        }


class SendOTPIPThrottle(OTPIPThrottle):
    scope = "otp_send_ip"


class SendOTPMobileThrottle(OTPMobileThrottle):
    scope = "otp_send_mobile"


class VerifyOTPIPThrottle(OTPIPThrottle):
    scope = "otp_verify_ip"


class VerifyOTPMobileThrottle(OTPMobileThrottle):
    scope = "otp_verify_mobile"
