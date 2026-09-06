from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from my1stapp.middleware import My1stAppLocaleMiddleware
from my1stapp.models import UserProfile

User = get_user_model()


class My1stAppLocaleMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.middleware = My1stAppLocaleMiddleware(lambda request: request)

        self.user = User.objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

    def test_admin_uses_english(self):
        request = self.factory.get("/admin/")

        request.user = self.user

        response = self.middleware(request)

        self.assertEqual(
            request.LANGUAGE_CODE,
            "en-gb",
        )

        self.assertEqual(
            response,
            request,
        )

    def test_unauthenticated_user_uses_default_language(self):
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {"is_authenticated": False},
        )()

        response = self.middleware(request)

        self.assertEqual(
            request.LANGUAGE_CODE,
            settings.LANGUAGE_CODE,
        )

        self.assertEqual(
            response,
            request,
        )

    def test_authenticated_user_uses_profile_language(self):
        profile = UserProfile.objects.get(
            user=self.user,
        )

        profile.language = "fr"
        profile.save()

        fresh_user = User.objects.get(
            pk=self.user.pk,
        )

        request = self.factory.get("/")

        request.user = fresh_user

        response = self.middleware(request)

        self.assertEqual(
            request.LANGUAGE_CODE,
            "fr",
        )

        self.assertEqual(
            response,
            request,
        )

    def test_authenticated_user_without_profile_uses_default_language(self):
        UserProfile.objects.filter(
            user=self.user,
        ).delete()

        fresh_user = User.objects.get(
            pk=self.user.pk,
        )

        self.assertFalse(
            UserProfile.objects.filter(
                user=fresh_user,
            ).exists()
        )

        request = self.factory.get("/")

        request.user = fresh_user

        response = self.middleware(request)

        self.assertEqual(
            request.LANGUAGE_CODE,
            settings.LANGUAGE_CODE,
        )

        self.assertEqual(
            response,
            request,
        )
