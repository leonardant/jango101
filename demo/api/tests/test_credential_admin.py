import json

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from api.credential_admin import APIClientCredentialAdmin
from api.models import APIClientCredential

User = get_user_model()


class APIClientCredentialAdminTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.model_admin = APIClientCredentialAdmin(
            APIClientCredential,
            admin.site,
        )

        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="TestPassword123!",
        )

        self.user = User.objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

        self.credential = APIClientCredential.objects.get(
            user=self.user,
        )

    def test_get_model_perms_returns_empty_dictionary(self):
        request = self.factory.get("/admin/")

        result = self.model_admin.get_model_perms(request)

        self.assertEqual(
            result,
            {},
        )

    def test_media_includes_custom_css_and_javascript(self):
        media = self.model_admin.media

        media_string = str(media)

        self.assertIn(
            "admin/css/api_admin",
            media_string,
        )

        self.assertIn(
            "admin/js/api_credentials",
            media_string,
        )

    def test_user_display_returns_dash_without_object(self):
        result = self.model_admin.user_display(None)

        self.assertEqual(
            result,
            "-",
        )

    def test_user_display_returns_username(self):
        result = self.model_admin.user_display(
            self.credential,
        )

        self.assertEqual(
            result,
            self.user.username,
        )

    def test_client_secret_display_returns_dash_without_object(self):
        result = self.model_admin.client_secret_display(None)

        self.assertEqual(
            result,
            "-",
        )

    def test_client_secret_display_contains_regenerate_button(self):
        result = self.model_admin.client_secret_display(
            self.credential,
        )

        result_string = str(result)

        self.assertIn(
            "Generate new secret",
            result_string,
        )

        self.assertIn(
            "regenerate-secret",
            result_string,
        )

    def test_regenerate_secret_view_rejects_get_requests(self):
        request = self.factory.get(
            f"/admin/api/apiclientcredential/{self.credential.pk}/regenerate-secret/"
        )

        request.user = self.admin_user

        response = self.model_admin.regenerate_secret_view(
            request,
            self.credential.pk,
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_regenerate_secret_view_returns_404_for_missing_credential(self):
        request = self.factory.post(
            "/admin/api/apiclientcredential/99999/regenerate-secret/"
        )

        request.user = self.admin_user

        response = self.model_admin.regenerate_secret_view(
            request,
            99999,
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_regenerate_secret_view_regenerates_secret(self):
        request = self.factory.post(
            f"/admin/api/apiclientcredential/{self.credential.pk}/regenerate-secret/"
        )

        request.user = self.admin_user

        response = self.model_admin.regenerate_secret_view(
            request,
            self.credential.pk,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response_data = json.loads(response.content.decode("utf-8"))

        self.assertIn(
            "client_secret",
            response_data,
        )

        self.assertTrue(
            response_data["client_secret"],
        )

        self.assertTrue(
            LogEntry.objects.filter(
                object_id=str(self.user.pk),
                change_message="API client secret regenerated.",
            ).exists()
        )
