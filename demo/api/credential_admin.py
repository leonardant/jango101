from django.contrib import admin
from django.contrib.admin.models import (
    CHANGE,
    LogEntry,
)
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.http import (
    HttpResponseNotAllowed,
    JsonResponse,
)

from django.urls import (
    path,
    reverse,
)

from django.utils.html import format_html

from .models import APIClientCredential
from .services.credentials import (
    regenerate_client_secret,
)


# ============================================================
# API CLIENT CREDENTIAL ADMIN
# ============================================================

@admin.register(APIClientCredential)
class APIClientCredentialAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "client_id",
        "active",
        "created_at",
    )

    readonly_fields = (
        "user_display",
        "client_secret_display",
        "client_id",
        "created_at",
        "updated_at",
    )

    fields = (
        "user_display",
        "client_secret_display",
        "active",
        "client_id",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "user__username",
        "client_id",
    )

    # =====================================
    # Hide from Django admin navigation
    # =====================================

    def get_model_perms(
        self,
        request,
    ):

        return {}

    # =====================================
    # CSS and JavaScript
    # =====================================

    class Media:

        css = {
            "all": (
                "admin/css/api_admin.css",
            )
        }

        js = (
            "admin/js/api_credentials.js",
        )

    # =====================================
    # User display
    # =====================================

    @admin.display(
        description="User"
    )
    def user_display(
        self,
        obj,
    ):

        if not obj:
            return "-"

        return obj.user.username

    # =====================================
    # Client secret display
    # =====================================

    @admin.display(
        description="Client secret"
    )
    def client_secret_display(
        self,
        obj,
    ):

        if not obj:
            return "-"

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[
                obj.pk,
            ],
        )

        return format_html(
            """
            <div class="client-secret-display">

                <span class="masked-secret">
                    ********
                </span>

                <button
                    type="button"
                    class="button regenerate-secret-button"
                    data-url="{}"
                >
                    Generate new secret
                </button>

            </div>
            """,
            url,
        )

    # =====================================
    # Custom admin URLs
    # =====================================

    def get_urls(
        self,
    ):

        urls = super().get_urls()

        custom_urls = [

            path(
                "<int:credential_id>/regenerate-secret/",
                self.admin_site.admin_view(
                    self.regenerate_secret_view
                ),
                name=(
                    "api_apiclientcredential_regenerate_secret"
                ),
            ),

        ]

        return custom_urls + urls

    # =====================================
    # Regenerate client secret
    # =====================================

    def regenerate_secret_view(
        self,
        request,
        credential_id,
    ):

        if request.method != "POST":

            return HttpResponseNotAllowed(
                ["POST"]
            )

        credential = self.get_object(
            request,
            credential_id,
        )

        if credential is None:

            return JsonResponse(
                {
                    "error": (
                        "Credential not found."
                    ),
                },
                status=404,
            )

        # Regenerate through the service layer

        raw_secret = regenerate_client_secret(
            credential
        )

        # Add this event to the user's
        # Django admin history

        self.log_user_api_event(
            request=request,
            user=credential.user,
            message=(
                "API client secret regenerated."
            ),
        )

        # Return the raw secret ONCE

        return JsonResponse(
            {
                "client_secret": raw_secret,
            }
        )

    # =====================================
    # Add API events to User history
    # =====================================

    def log_user_api_event(
        self,
        request,
        user,
        message,
    ):

        LogEntry.objects.create(

            user_id=request.user.pk,

            content_type=(
                ContentType.objects.get_for_model(
                    User
                )
            ),

            object_id=str(
                user.pk
            ),

            object_repr=str(
                user
            ),

            action_flag=CHANGE,

            change_message=message,

        )