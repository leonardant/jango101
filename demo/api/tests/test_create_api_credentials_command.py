from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from api.models import APIClientCredential

User = get_user_model()


class CreateAPICredentialsCommandTests(TestCase):
    def test_command_raises_error_when_user_does_not_exist(self):
        with self.assertRaisesMessage(
            CommandError,
            'User "missinguser" does not exist.',
        ):
            call_command(
                "create_api_credentials",
                "missinguser",
            )

    def test_command_warns_when_credentials_already_exist(self):
        user = User.objects.create_user(
            username="existinguser",
            password="TestPassword123!",
        )

        self.assertTrue(
            APIClientCredential.objects.filter(
                user=user,
            ).exists()
        )

        output = StringIO()

        call_command(
            "create_api_credentials",
            user.username,
            stdout=output,
        )

        self.assertIn(
            f"API credentials already exist for {user.username}.",
            output.getvalue(),
        )

        self.assertIn(
            "Create new credentials only after rotating or deleting "
            "the existing credentials.",
            output.getvalue(),
        )

    def test_command_creates_credentials_when_none_exist(self):
        user = User.objects.create_user(
            username="newcredentialuser",
            password="TestPassword123!",
        )

        APIClientCredential.objects.filter(
            user=user,
        ).delete()

        self.assertFalse(
            APIClientCredential.objects.filter(
                user=user,
            ).exists()
        )

        output = StringIO()

        call_command(
            "create_api_credentials",
            user.username,
            stdout=output,
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.assertTrue(
            credential.client_id,
        )

        self.assertTrue(
            credential.client_secret,
        )

        self.assertIn(
            f"API credentials created for {user.username}",
            output.getvalue(),
        )

        self.assertIn(
            f"Client ID: {credential.client_id}",
            output.getvalue(),
        )

        self.assertIn(
            "Client Secret:",
            output.getvalue(),
        )

        self.assertIn(
            "IMPORTANT: Save the client secret now. It cannot be recovered later.",
            output.getvalue(),
        )

    def test_command_creates_only_one_credential(self):
        user = User.objects.create_user(
            username="singlecredentialuser",
            password="TestPassword123!",
        )

        APIClientCredential.objects.filter(
            user=user,
        ).delete()

        call_command(
            "create_api_credentials",
            user.username,
        )

        self.assertEqual(
            APIClientCredential.objects.filter(
                user=user,
            ).count(),
            1,
        )
