from django import forms

from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE

from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.forms import (
    UserChangeForm,
    UserCreationForm,
)

from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType

from django.http import (
    JsonResponse,
    HttpResponseNotAllowed,
)

from django.urls import (
    path,
    reverse,
)

from django.utils.html import format_html

from django.utils.safestring import mark_safe

from my1stapp.models import UserProfile

from .models import APIClientCredential


# ============================================================
# USER CREATION FORM
# ============================================================

class CustomUserCreationForm(UserCreationForm):

    language = forms.ChoiceField(
        choices=UserProfile.LANGUAGE_CHOICES,
        initial="en-gb",
        label="Preferred language / culture",
        required=True,
    )

    class Meta(UserCreationForm.Meta):

        model = User

        fields = (
            "username",
            "language",
        )

    def save(self, commit=True):

        user = super().save(commit=commit)

        if commit:

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "language": self.cleaned_data[
                        "language"
                    ],
                },
            )

        return user


# ============================================================
# USER CHANGE FORM
# ============================================================

class CustomUserChangeForm(UserChangeForm):

    language = forms.ChoiceField(
        choices=UserProfile.LANGUAGE_CHOICES,
        label="Preferred language / culture",
        required=True,
    )

    class Meta(UserChangeForm.Meta):

        model = User

        fields = "__all__"

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:

            profile, created = (
                UserProfile.objects.get_or_create(
                    user=self.instance,
                    defaults={
                        "language": "en-gb",
                    },
                )
            )

            self.fields[
                "language"
            ].initial = profile.language

    def save(self, commit=True):

        user = super().save(commit=commit)

        if commit:

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "language": self.cleaned_data[
                        "language"
                    ],
                },
            )

        return user


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

    def get_urls(self):

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

        # Add this event to the user's
        # Django admin history

        self.log_user_api_event(
            request=request,
            user=credential.user,
            message=(
                "API client secret regenerated."
            ),
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

            content_type=(
                ContentType.objects.get_for_model(
                    User
                )
            ),

            object_id=str(user.pk),

            object_repr=str(user),

            action_flag=CHANGE,

            change_message=message,

        )


# ============================================================
# CUSTOM USER ADMIN
# ============================================================

# Remove Django's default User admin registration

admin.site.unregister(User)


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

        css = {
            "all": (
                "admin/css/api_admin.css",
            )
        }

        js = (
            "admin/js/api_credentials.js",
        )

    # =====================================
    # ADD USER PAGE
    # =====================================

    add_fieldsets = (

        (
            None,
            {
                "classes": (
                    "wide",
                ),

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

        for index, fieldset in enumerate(
            fieldsets
        ):

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

                    fields.append(
                        "language"
                    )

                options["fields"] = tuple(
                    fields
                )

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
                "fields": (
                    "api_credentials_display",
                ),
            },

        )

        # ---------------------------------
        # Insert before Important dates
        # ---------------------------------

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

            fieldsets.append(
                api_credentials_fieldset
            )

        return fieldsets

    # =====================================
    # API credential section
    # =====================================

    @admin.display(
        description="API client credentials"
    )
    def api_credentials_display(
        self,
        obj,
    ):

        if not obj:

            return "-"

        try:

            credential = (
                APIClientCredential.objects.get(
                    user=obj
                )
            )

        except APIClientCredential.DoesNotExist:

            return mark_safe(
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

            credential.created_at.strftime(
                "%b. %-d, %Y, %-I:%M %p"
            ),

            credential.updated_at.strftime(
                "%b. %-d, %Y, %-I:%M %p"
            ),
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

            readonly_fields.append(
                "api_credentials_display"
            )

        return readonly_fields