from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models import APIClientCredential
from my1stapp.models import UserProfile


User = get_user_model()


class UserCreationTests(TestCase):

    def test_new_user_gets_user_profile(self):

        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.assertTrue(
            UserProfile.objects.filter(
                user=user,
            ).exists()
        )

    def test_new_user_profile_uses_default_language(self):

        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        profile = UserProfile.objects.get(
            user=user,
        )

        self.assertEqual(
            profile.language,
            "en-gb",
        )

    def test_new_user_gets_api_client_credentials(self):

        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        self.assertTrue(
            APIClientCredential.objects.filter(
                user=user,
            ).exists()
        )

    def test_new_user_has_exactly_one_user_profile(self):

        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        profile_count = UserProfile.objects.filter(
            user=user,
        ).count()

        self.assertEqual(
            profile_count,
            1,
        )

    def test_new_user_has_exactly_one_api_credential(self):

        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        credential_count = APIClientCredential.objects.filter(
            user=user,
        ).count()

        self.assertEqual(
            credential_count,
            1,
        )

    def test_api_credential_has_client_id(self):

        user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        credential = APIClientCredential.objects.get(
            user=user,
        )

        self.assertTrue(
            credential.client_id
        )