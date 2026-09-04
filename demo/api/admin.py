from django.contrib import admin

from .models import APIClientCredential


@admin.register(APIClientCredential)
class APIClientCredentialAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "client_id",
        "active",
        "created_at",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "user__username",
        "client_id",
    )

    readonly_fields = (
        "client_id",
        "created_at",
        "updated_at",
    )