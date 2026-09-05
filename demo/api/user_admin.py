from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html

from .admin_forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
)
from .models import APIClientCredential

User = get_user_model()

# ============================================================
# CUSTOM USER ADMIN
# ============================================================


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # =====================================
    # Custom forms
    # =====================================

    add_form = CustomUserCreationForm

    form = CustomUserChangeForm

    # =====================================
    # CSS and JavaScript
    # =====================================

    class Media:
        css = {"all": ("admin/css/api_admin.css",)}

        js = ("admin/js/api_credentials.js",)

    # =====================================
    # ADD USER PAGE
    # =====================================

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "language",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # =====================================
    # CHANGE USER PAGE
    # =====================================

    def get_fieldsets(
        self,
        request,
        obj=None,
    ):

        # ---------------------------------
        # ADD USER
        # ---------------------------------

        if obj is None:
            return self.add_fieldsets

        # ---------------------------------
        # EDIT EXISTING USER
        # ---------------------------------

        fieldsets = list(
            super().get_fieldsets(
                request,
                obj,
            )
        )

        # ---------------------------------
        # Add language to Personal info
        # ---------------------------------

        for index, fieldset in enumerate(fieldsets):
            title = fieldset[0]

            options = fieldset[1].copy()

            fields = list(
                options.get(
                    "fields",
                    (),
                )
            )

            if title == "Personal info":
                if "language" not in fields:
                    fields.append("language")

                options["fields"] = tuple(fields)

                fieldsets[index] = (
                    title,
                    options,
                )

                break

        # ---------------------------------
        # API credentials section
        # ---------------------------------

        api_credentials_fieldset = (
            "API client credentials",
            {
                "fields": ("api_credentials_display",),
            },
        )

        # ---------------------------------
        # Insert before Important dates
        # ---------------------------------

        for index, fieldset in enumerate(fieldsets):
            if fieldset[0] == "Important dates":
                fieldsets.insert(
                    index,
                    api_credentials_fieldset,
                )

                break

        else:
            fieldsets.append(api_credentials_fieldset)

        return fieldsets

    # =====================================
    # API credential section
    # =====================================

    @admin.display(description="API client credentials")
    def api_credentials_display(
        self,
        obj,
    ):

        if not obj:
            return "-"

        try:
            credential = APIClientCredential.objects.get(user=obj)

        except APIClientCredential.DoesNotExist:
            return format_html(
                """
                <div class="api-credentials-empty">
                    No API client credential exists
                    for this user.
                </div>
                """
            )

        regenerate_url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[
                credential.pk,
            ],
        )

        active_display = "✓" if credential.active else "✗"

        active_class = "api-active" if credential.active else "api-inactive"

        return format_html(
            """
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
            """,
            regenerate_url,
            active_class,
            active_display,
            credential.client_id,
            credential.created_at.strftime("%b. %-d, %Y, %-I:%M %p"),
            credential.updated_at.strftime("%b. %-d, %Y, %-I:%M %p"),
        )

    # =====================================
    # Read-only custom display
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

        if obj is not None:
            readonly_fields.append("api_credentials_display")

        return readonly_fields
