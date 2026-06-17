from django.test import override_settings
from rest_framework.test import APITestCase

from django.core.cache import cache


TEST_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


TEST_THROTTLES = {
    "DEFAULT_THROTTLE_RATES": {
        "otp_send_ip": "1/min",
        "otp_send_mobile": "1/min",
        "otp_verify_ip": "1/min",
        "otp_verify_mobile": "1/min",
    }
}


@override_settings(CACHES=TEST_CACHE, REST_FRAMEWORK=TEST_THROTTLES)
class OTPThrottleTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_send_throttles_by_ip(self):
        payload = {"mobile": "09121234567", "otp": "123456"}

        first = self.client.post("/send/", payload, format="json")
        second = self.client.post("/send/", payload, format="json")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertIn("throttled", second.data["detail"].lower())

    def test_send_throttles_by_mobile_independently_of_ip(self):
        mobile = "09121234567"
        first = self.client.post(
            "/send/",
            {"mobile": mobile, "otp": "123456"},
            format="json",
            REMOTE_ADDR="10.0.0.1",
        )
        second = self.client.post(
            "/send/",
            {"mobile": mobile, "otp": "654321"},
            format="json",
            REMOTE_ADDR="10.0.0.2",
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertIn("throttled", second.data["detail"].lower())

    def test_verify_has_its_own_throttle_scope(self):
        payload = {"mobile": "09121234567", "otp": "123456"}

        send_first = self.client.post("/send/", payload, format="json")
        verify_first = self.client.post("/verify/", payload, format="json")
        verify_second = self.client.post("/verify/", payload, format="json")

        self.assertEqual(send_first.status_code, 200)
        self.assertEqual(verify_first.status_code, 200)
        self.assertEqual(verify_second.status_code, 429)
        self.assertIn("throttled", verify_second.data["detail"].lower())
