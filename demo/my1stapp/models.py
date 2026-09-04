from django.conf import settings
from django.db import models


class ToDoItem(models.Model):

    title = models.CharField(
        max_length=100,
    )

    description = models.TextField()

    completed = models.BooleanField(
        default=False,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="todo_items",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.title


class UserProfile(models.Model):

    LANGUAGE_CHOICES = [
        ("en-gb", "English (United Kingdom)"),
        ("fr", "Français"),
        ("de", "Deutsch"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="en-gb",
    )

    def __str__(self):
        return self.user.username