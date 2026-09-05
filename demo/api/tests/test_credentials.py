from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse

from api.models import APIClientCredential

User = get_user_model()


class APIClientCredentialTests(TestCase):
    # =====================================
    # Credential creation tests
    # =====================================

    def test_credential_is_created_for_new_user(self):

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        self.assertTrue(
            APIClientCredential.objects.filter(
                user=user,
            ).exists()
        )

    def test_credential_has_client_id(self):

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.assertTrue(credential.client_id)

    def test_client_id_is_unique(self):

        user_one = User.objects.create_user(
            username="userone",
            password="TestPassword123!",
        )

        user_two = User.objects.create_user(
            username="usertwo",
            password="TestPassword123!",
        )

        credential_one = APIClientCredential.objects.get(
            user=user_one,
        )

        credential_two = APIClientCredential.objects.get(
            user=user_two,
        )

        self.assertNotEqual(
            credential_one.client_id,
            credential_two.client_id,
        )

    def test_credential_has_client_secret(self):

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.assertTrue(credential.client_secret)

    def test_new_credential_is_active_by_default(self):

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.assertTrue(credential.active)

    def test_user_can_only_have_one_credential(self):

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential_count = APIClientCredential.objects.filter(
            user=user,
        ).count()

        self.assertEqual(
            credential_count,
            1,
        )

    # =====================================
    # Client secret hashing tests
    # =====================================

    def test_generated_client_secret_is_hashed(self):

        raw_secret = APIClientCredential.generate_client_secret()

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        credential.set_client_secret(raw_secret)

        credential.save()

        credential.refresh_from_db()

        self.assertNotEqual(
            credential.client_secret,
            raw_secret,
        )

    def test_correct_client_secret_validates(self):

        raw_secret = APIClientCredential.generate_client_secret()

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        credential.set_client_secret(raw_secret)

        credential.save()

        credential.refresh_from_db()

        self.assertTrue(
            check_password(
                raw_secret,
                credential.client_secret,
            )
        )

    def test_incorrect_client_secret_does_not_validate(self):

        raw_secret = APIClientCredential.generate_client_secret()

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        credential.set_client_secret(raw_secret)

        credential.save()

        credential.refresh_from_db()

        self.assertFalse(
            check_password(
                "this-is-the-wrong-secret",
                credential.client_secret,
            )
        )

    # =====================================
    # Secret regeneration model tests
    # =====================================

    def test_regenerating_secret_changes_stored_hash(self):

        first_secret = APIClientCredential.generate_client_secret()

        second_secret = APIClientCredential.generate_client_secret()

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        credential.set_client_secret(first_secret)

        credential.save()

        first_hash = credential.client_secret

        credential.set_client_secret(second_secret)

        credential.save()

        credential.refresh_from_db()

        self.assertNotEqual(
            credential.client_secret,
            first_hash,
        )

    def test_old_secret_does_not_work_after_regeneration(self):

        old_secret = APIClientCredential.generate_client_secret()

        new_secret = APIClientCredential.generate_client_secret()

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        credential.set_client_secret(old_secret)

        credential.save()

        credential.set_client_secret(new_secret)

        credential.save()

        credential.refresh_from_db()

        self.assertFalse(
            check_password(
                old_secret,
                credential.client_secret,
            )
        )

    def test_new_secret_works_after_regeneration(self):

        old_secret = APIClientCredential.generate_client_secret()

        new_secret = APIClientCredential.generate_client_secret()

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        credential.set_client_secret(old_secret)

        credential.save()

        credential.set_client_secret(new_secret)

        credential.save()

        credential.refresh_from_db()

        self.assertTrue(
            check_password(
                new_secret,
                credential.client_secret,
            )
        )

    # =====================================
    # Admin regeneration endpoint tests
    # =====================================

    def test_unauthenticated_user_cannot_regenerate_secret(self):

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_non_staff_user_cannot_regenerate_secret(self):

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.client.login(
            username="credentialuser",
            password="TestPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_regenerate_secret_endpoint_rejects_get_request(self):

        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.client.login(
            username="adminuser",
            password="AdminPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_admin_can_regenerate_secret(self):

        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.client.login(
            username="adminuser",
            password="AdminPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_regenerate_secret_endpoint_returns_client_secret(self):

        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.client.login(
            username="adminuser",
            password="AdminPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.post(url)

        response_data = response.json()

        self.assertIn(
            "client_secret",
            response_data,
        )

        self.assertTrue(response_data["client_secret"])

    def test_regenerated_secret_matches_stored_hash(self):

        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.client.login(
            username="adminuser",
            password="AdminPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.post(url)

        response_data = response.json()

        new_secret = response_data["client_secret"]

        credential.refresh_from_db()

        self.assertTrue(
            check_password(
                new_secret,
                credential.client_secret,
            )
        )

    def test_regenerating_secret_changes_stored_secret(self):

        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        old_hash = credential.client_secret

        self.client.login(
            username="adminuser",
            password="AdminPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            200,
        )

        credential.refresh_from_db()

        self.assertNotEqual(
            credential.client_secret,
            old_hash,
        )

    def test_old_secret_is_invalid_after_endpoint_regeneration(self):

        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        user = User.objects.create_user(
            username="credentialuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        old_secret = APIClientCredential.generate_client_secret()

        credential.set_client_secret(old_secret)

        credential.save()

        self.client.login(
            username="adminuser",
            password="AdminPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[credential.pk],
        )

        response = self.client.post(url)

        response_data = response.json()

        new_secret = response_data["client_secret"]

        credential.refresh_from_db()

        self.assertFalse(
            check_password(
                old_secret,
                credential.client_secret,
            )
        )

        self.assertTrue(
            check_password(
                new_secret,
                credential.client_secret,
            )
        )

    def test_regenerate_secret_returns_404_for_missing_credential(self):

        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!",
        )

        self.client.login(
            username="adminuser",
            password="AdminPassword123!",
        )

        url = reverse(
            "admin:api_apiclientcredential_regenerate_secret",
            args=[999999],
        )

        response = self.client.post(url)

        self.assertEqual(
            response.status_code,
            404,
        )
