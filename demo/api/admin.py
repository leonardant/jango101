from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.http import JsonResponse, HttpResponseNotAllowed
from django.urls import path, reverse
from django.utils.html import format_html

from .models import APIClientCredential


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

    def get_model_perms(self, request):

        return {}

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

    @admin.display(description="User")
    def user_display(self, obj):

        if not obj:
            return "-"

        return obj.user.username

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

        raw_secret = (
            APIClientCredential.generate_client_secret()
        )

        credential.set_client_secret(
            raw_secret
        )

        credential.save(
            update_fields=[
                "client_secret",
                "updated_at",
            ]
        )
        # Add this action to the user's
        # Django admin history

        self.log_user_api_event(
            request=request,
            user=credential.user,
            message="API client secret regenerated.",
        )

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

            content_type=ContentType.objects.get_for_model(
                User
            ),

            object_id=str(user.pk),

            object_repr=str(user),

            action_flag=CHANGE,

            change_message=message,
        )

# ============================================================
# CUSTOM USER ADMIN
# ============================================================

# Remove Django's existing User admin registration
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # =====================================
    # Include our CSS and JavaScript
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
    # API credential section
    # =====================================

    @admin.display(description="API client credentials")
    def api_credentials_display(self, obj):

        try:

            credential = APIClientCredential.objects.get(
                user=obj
            )

        except APIClientCredential.DoesNotExist:

            return format_html(
                '''
                <div class="api-credentials-empty">
                    No API client credential exists for this user.
                </div>
                '''
            )

        regenerate_url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        active_display = (
            "✓"
            if credential.active
            else "✗"
        )

        active_class = (
            "api-active"
            if credential.active
            else "api-inactive"
        )

        return format_html(
            '''
            <div class="embedded-api-credentials">

                <div class="api-credential-row">

                    <div class="api-credential-label">
                        Client secret:
                    </div>

                    <div class="api-credential-value">

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

                </div>


                <div class="api-credential-row">

                    <div class="api-credential-label">
                        Active:
                    </div>

                    <div class="api-credential-value {}">
                        {}
                    </div>

                </div>


                <div class="api-credential-row">

                    <div class="api-credential-label">
                        Client ID:
                    </div>

                    <div class="api-credential-value api-client-id">
                        {}
                    </div>

                </div>


                <div class="api-credential-row">

                    <div class="api-credential-label">
                        Created at:
                    </div>

                    <div class="api-credential-value">
                        {}
                    </div>

                </div>


                <div class="api-credential-row">

                    <div class="api-credential-label">
                        Updated at:
                    </div>

                    <div class="api-credential-value">
                        {}
                    </div>

                </div>

            </div>
            ''',

            regenerate_url,

            active_class,
            active_display,

            credential.client_id,

            credential.created_at.strftime(
                "%b. %-d, %Y, %-I:%M %p"
            ),

            credential.updated_at.strftime(
                "%b. %-d, %Y, %-I:%M %p"
            ),
        )

    # =====================================
    # Position API credentials before
    # Important dates
    # =====================================

    def get_fieldsets(
        self,
        request,
        obj=None,
    ):

        fieldsets = list(
            super().get_fieldsets(
                request,
                obj,
            )
        )

        api_credentials_fieldset = (
            "API client credentials",
            {
                "fields": (
                    "api_credentials_display",
                ),
            },
        )

        # Insert immediately before
        # Django's "Important dates" section

        for index, fieldset in enumerate(
            fieldsets
        ):

            if fieldset[0] == "Important dates":

                fieldsets.insert(
                    index,
                    api_credentials_fieldset,
                )

                break

        else:

            # Fallback if Important dates
            # cannot be found

            fieldsets.append(
                api_credentials_fieldset
            )

        return fieldsets

    # =====================================
    # Make custom display readonly
    # =====================================

    def get_readonly_fields(
        self,
        request,
        obj=None,
    ):

        readonly_fields = list(
            super().get_readonly_fields(
                request,
                obj,
            )
        )

        readonly_fields.append(
            "api_credentials_display"
        )

        return readonly_fields