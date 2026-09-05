import secrets

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models


class APIClientCredential(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_client_credential",
    )

    client_id = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
    )

    client_secret = models.CharField(
        max_length=255,
        editable=False,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @staticmethod
    def generate_client_id():
        return secrets.token_urlsafe(24)

    @staticmethod
    def generate_client_secret():
        return secrets.token_urlsafe(48)

    def set_client_secret(self, raw_secret):
        self.client_secret = make_password(raw_secret)

    def save(self, *args, **kwargs):

        if not self.client_id:
            self.client_id = self.generate_client_id()

        if not self.client_secret:
            raw_secret = self.generate_client_secret()
            self.set_client_secret(raw_secret)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.client_id})"
