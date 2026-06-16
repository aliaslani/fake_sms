# fake_sms/models.py

from django.db import models
from django.utils import timezone
from datetime import timedelta


class OTPRecord(models.Model):
    mobile = models.CharField(max_length=15, db_index=True)
    otp = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    is_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["mobile"]),
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)

        super().save(*args, **kwargs)

    @property
    def expired(self):
        return timezone.now() > self.expires_at