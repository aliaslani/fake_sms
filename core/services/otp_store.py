# fake_sms/services/otp_store.py

from django.core.cache import cache


class OTPStoreService:
    PREFIX = "fake_sms"

    @classmethod
    def save(cls, mobile: str, otp: str, ttl=300):
        key = f"{cls.PREFIX}:{mobile}"

        cache.set(
            key,
            {
                "otp": otp
            },
            timeout=ttl
        )

    @classmethod
    def get(cls, mobile: str):
        return cache.get(f"{cls.PREFIX}:{mobile}")

    @classmethod
    def verify(cls, mobile: str, otp: str):
        data = cls.get(mobile)

        if not data:
            return False

        if data["otp"] != otp:
            return False

        cache.delete(f"{cls.PREFIX}:{mobile}")

        return True