from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import APIClientCredential


User = get_user_model()


@receiver(post_save, sender=User)
def create_api_client_credential(sender, instance, created, **kwargs):
    """
    Automatically create API credentials for every new user.
    """

    if created:
        APIClientCredential.objects.get_or_create(user=instance)
