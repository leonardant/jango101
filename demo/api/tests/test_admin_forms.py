from django.contrib.auth import get_user_model
from django.test import TestCase
from my1stapp.models import UserProfile

from api.admin_forms import (
    CustomUserChangeForm,
    CustomUserCreationForm,
)

User = get_user_model()


class CustomUserCreationFormTests(TestCase):
    def test_valid_form_creates_user_and_profile(self):
        form = CustomUserCreationForm(
            data={
                "username": "new_user",
                "language": "en-gb",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        user = form.save()

        self.assertEqual(
            user.username,
            "new_user",
        )

        profile = UserProfile.objects.get(
            user=user,
        )

        self.assertEqual(
            profile.language,
            "en-gb",
        )

    def test_save_with_commit_false_does_not_create_profile(self):
        form = CustomUserCreationForm(
            data={
                "username": "unsaved_user",
                "language": "en-gb",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        user = form.save(
            commit=False,
        )

        self.assertIsNone(
            user.pk,
        )

        self.assertFalse(
            UserProfile.objects.filter(
                user__username="unsaved_user",
            ).exists()
        )


class CustomUserChangeFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

    def test_initialises_language_from_existing_profile(self):
        profile = UserProfile.objects.get(
            user=self.user,
        )

        profile.language = "fr"

        profile.save()

        form = CustomUserChangeForm(
            instance=self.user,
        )

        self.assertEqual(
            form.fields["language"].initial,
            "fr",
        )

    def test_creates_missing_profile_when_initialised(self):
        UserProfile.objects.filter(
            user=self.user,
        ).delete()

        self.assertFalse(
            UserProfile.objects.filter(
                user=self.user,
            ).exists()
        )

        form = CustomUserChangeForm(
            instance=self.user,
        )

        self.assertTrue(
            UserProfile.objects.filter(
                user=self.user,
            ).exists()
        )

        self.assertEqual(
            form.fields["language"].initial,
            "en-gb",
        )

    def test_unsaved_user_does_not_create_profile_when_initialised(self):
        unsaved_user = User(
            username="unsaved_user",
        )

        form = CustomUserChangeForm(
            instance=unsaved_user,
        )

        self.assertEqual(
            form.instance,
            unsaved_user,
        )

        self.assertIsNone(
            unsaved_user.pk,
        )

        self.assertFalse(
            UserProfile.objects.filter(
                user__username="unsaved_user",
            ).exists()
        )

    def test_save_updates_profile_language(self):
        profile = UserProfile.objects.get(
            user=self.user,
        )

        profile.language = "en-gb"

        profile.save()

        form = CustomUserChangeForm(
            instance=self.user,
            data={
                "username": self.user.username,
                "password": self.user.password,
                "date_joined": (
                    self.user.date_joined.strftime(
                        "%Y-%m-%d %H:%M:%S",
                    )
                ),
                "language": "fr",
            },
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        form.save()

        profile.refresh_from_db()

        self.assertEqual(
            profile.language,
            "fr",
        )

    def test_save_with_commit_false_does_not_update_profile(self):
        profile = UserProfile.objects.get(
            user=self.user,
        )

        profile.language = "en-gb"

        profile.save()

        form = CustomUserChangeForm(
            instance=self.user,
            data={
                "username": self.user.username,
                "password": self.user.password,
                "date_joined": (
                    self.user.date_joined.strftime(
                        "%Y-%m-%d %H:%M:%S",
                    )
                ),
                "language": "fr",
            },
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        user = form.save(
            commit=False,
        )

        self.assertEqual(
            user,
            self.user,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.language,
            "en-gb",
        )
