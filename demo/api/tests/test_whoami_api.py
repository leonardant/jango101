from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class WhoAmIAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="TestPassword123!",
        )

        self.whoami_url = "/api/whoami/"

    def test_unauthenticated_user_cannot_access_whoami(self):
        response = self.client.get(
            self.whoami_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_access_whoami(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            self.whoami_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.user.id,
        )

        self.assertEqual(
            response.data["username"],
            self.user.username,
        )

        self.assertEqual(
            response.data["email"],
            self.user.email,
        )
