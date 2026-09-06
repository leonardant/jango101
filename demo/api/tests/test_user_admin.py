from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from api.models import APIClientCredential
from api.user_admin import CustomUserAdmin

User = get_user_model()


class CustomUserAdminTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.model_admin = CustomUserAdmin(
            User,
            admin.site,
        )

        self.request = self.factory.get("/admin/")

        self.user = User.objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

    def test_media_includes_custom_css_and_javascript(self):
        media = self.model_admin.media

        media_string = str(media)

        self.assertIn(
            "api_admin",
            media_string,
        )

        self.assertIn(
            "api_credentials",
            media_string,
        )

    def test_get_fieldsets_for_new_user_returns_add_fieldsets(self):
        fieldsets = self.model_admin.get_fieldsets(
            self.request,
            obj=None,
        )

        self.assertEqual(
            fieldsets,
            self.model_admin.add_fieldsets,
        )

    def test_get_fieldsets_for_existing_user_includes_language(self):
        fieldsets = self.model_admin.get_fieldsets(
            self.request,
            obj=self.user,
        )

        personal_info_fields = None

        for title, options in fieldsets:
            if title == "Personal info":
                personal_info_fields = options["fields"]
                break

        self.assertIsNotNone(personal_info_fields)

        self.assertIn(
            "language",
            personal_info_fields,
        )

    def test_get_fieldsets_for_existing_user_includes_api_credentials_section(
        self,
    ):
        fieldsets = self.model_admin.get_fieldsets(
            self.request,
            obj=self.user,
        )

        titles = [fieldset[0] for fieldset in fieldsets]

        self.assertIn(
            "API client credentials",
            titles,
        )

    def test_api_credentials_display_returns_dash_without_user(self):
        result = self.model_admin.api_credentials_display(
            None,
        )

        self.assertEqual(
            result,
            "-",
        )

    def test_api_credentials_display_shows_message_without_credential(self):
        APIClientCredential.objects.filter(
            user=self.user,
        ).delete()

        self.assertFalse(
            APIClientCredential.objects.filter(
                user=self.user,
            ).exists()
        )

        result = self.model_admin.api_credentials_display(
            self.user,
        )

        self.assertIn(
            "No API client credential exists",
            str(result),
        )

    def test_api_credentials_display_shows_active_credential(self):
        APIClientCredential.objects.filter(
            user=self.user,
        ).delete()

        credential = APIClientCredential.objects.create(
            user=self.user,
            active=True,
        )

        result = self.model_admin.api_credentials_display(
            self.user,
        )

        regenerate_url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[
                credential.pk,
            ],
        )

        result_string = str(result)

        self.assertIn(
            credential.client_id,
            result_string,
        )

        self.assertIn(
            regenerate_url,
            result_string,
        )

        self.assertIn(
            "api-active",
            result_string,
        )

        self.assertIn(
            "✓",
            result_string,
        )

    def test_api_credentials_display_shows_inactive_credential(self):
        APIClientCredential.objects.filter(
            user=self.user,
        ).delete()

        credential = APIClientCredential.objects.create(
            user=self.user,
            active=False,
        )

        result = self.model_admin.api_credentials_display(
            self.user,
        )

        result_string = str(result)

        self.assertIn(
            credential.client_id,
            result_string,
        )

        self.assertIn(
            "api-inactive",
            result_string,
        )

        self.assertIn(
            "✗",
            result_string,
        )

    def test_get_readonly_fields_for_new_user(self):
        readonly_fields = self.model_admin.get_readonly_fields(
            self.request,
            obj=None,
        )

        self.assertNotIn(
            "api_credentials_display",
            readonly_fields,
        )

    def test_get_readonly_fields_for_existing_user(self):
        readonly_fields = self.model_admin.get_readonly_fields(
            self.request,
            obj=self.user,
        )

        self.assertIn(
            "api_credentials_display",
            readonly_fields,
        )
