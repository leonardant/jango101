from django.contrib import admin
from django.http import JsonResponse, HttpResponseNotAllowed
from django.urls import path, reverse
from django.utils.html import format_html

from .models import APIClientCredential


@admin.register(APIClientCredential)
class APIClientCredentialAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "client_id",
        "active",
        "created_at",
    )

    readonly_fields = (
        "client_secret_display",
        "client_id",
        "created_at",
        "updated_at",
    )

    fields = (
        "user",
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
    # Client secret display
    # =====================================

    @admin.display(description="Client secret")
    def client_secret_display(self, obj):

        if not obj:
            return "-"

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[obj.pk],
        )

        return format_html(
            '''
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
            ''',
            url,
        )

    # =====================================
    # Custom admin URLs
    # =====================================

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:credential_id>/regenerate-secret/",
                self.admin_site.admin_view(
                    self.regenerate_secret_view
                ),
                name="api_apiclientcredential_regenerate_secret",
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
                    "error": "Credential not found.",
                },
                status=404,
            )

        # Generate a new raw secret
        raw_secret = (
            APIClientCredential.generate_client_secret()
        )

        # Store only the hashed version
        credential.set_client_secret(
            raw_secret
        )

        credential.save(
            update_fields=[
                "client_secret",
                "updated_at",
            ]
        )

        # Return the raw secret ONCE
        return JsonResponse(
            {
                "client_secret": raw_secret,
            }
        )