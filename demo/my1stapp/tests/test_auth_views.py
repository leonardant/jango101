from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CustomPasswordChangeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="passworduser",
            password="OldPassword123!",
        )

        self.password_change_url = reverse(
            "password_change",
        )

        self.profile_url = reverse(
            "my1stapp:profile",
        )

    def test_password_change_requires_login(self):
        response = self.client.get(
            self.password_change_url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            reverse("login"),
            response.url,
        )

    def test_logged_in_user_can_view_password_change_form(self):
        self.client.login(
            username="passworduser",
            password="OldPassword123!",
        )

        response = self.client.get(
            self.password_change_url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "registration/password_change_form.html",
        )

    def test_user_can_change_password(self):
        self.client.login(
            username="passworduser",
            password="OldPassword123!",
        )

        response = self.client.post(
            self.password_change_url,
            {
                "old_password": "OldPassword123!",
                "new_password1": "NewPassword456!",
                "new_password2": "NewPassword456!",
            },
            follow=True,
        )

        self.assertRedirects(
            response,
            self.profile_url,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewPassword456!",
            )
        )

    def test_success_message_is_displayed_after_password_change(self):
        self.client.login(
            username="passworduser",
            password="OldPassword123!",
        )

        response = self.client.post(
            self.password_change_url,
            {
                "old_password": "OldPassword123!",
                "new_password1": "NewPassword456!",
                "new_password2": "NewPassword456!",
            },
            follow=True,
        )

        messages = list(
            response.context["messages"],
        )

        self.assertTrue(
            any(
                str(message) == "Your password was changed successfully."
                for message in messages
            )
        )
