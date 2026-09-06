from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase

from api.models import APIClientCredential

User = get_user_model()


class APIClientCredentialModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="credential_user",
            password="TestPassword123!",
        )

        self.credential = APIClientCredential.objects.get(
            user=self.user,
        )

    def test_generates_client_id_when_not_provided(self):
        self.assertTrue(self.credential.client_id)

        self.assertLessEqual(
            len(self.credential.client_id),
            64,
        )

    def test_generates_client_secret_when_not_provided(self):
        self.assertTrue(self.credential.client_secret)

    def test_generated_client_secret_is_hashed(self):
        self.assertNotEqual(
            self.credential.client_secret,
            "",
        )

        self.assertTrue(self.credential.client_secret.startswith("pbkdf2_"))

    def test_set_client_secret_hashes_raw_secret(self):
        raw_secret = "my-super-secret-value"

        self.credential.set_client_secret(raw_secret)

        self.assertNotEqual(
            self.credential.client_secret,
            raw_secret,
        )

        self.assertTrue(
            check_password(
                raw_secret,
                self.credential.client_secret,
            )
        )

    def test_save_preserves_existing_client_id(self):
        original_client_id = self.credential.client_id

        self.credential.save()

        self.credential.refresh_from_db()

        self.assertEqual(
            self.credential.client_id,
            original_client_id,
        )

    def test_save_preserves_existing_client_secret(self):
        original_secret = self.credential.client_secret

        self.credential.save()

        self.credential.refresh_from_db()

        self.assertEqual(
            self.credential.client_secret,
            original_secret,
        )

    def test_string_representation_contains_username_and_client_id(self):
        self.assertEqual(
            str(self.credential),
            (f"{self.user.username} ({self.credential.client_id})"),
        )
