from django.contrib.auth import get_user_model
from django.test import TestCase
from my1stapp.models import ToDoItem
from rest_framework import status
from rest_framework.test import APIClient

from api.models import APIClientCredential

User = get_user_model()


class ClientCredentialsAPITests(TestCase):
    def setUp(self):

        self.client = APIClient()

        # =====================================
        # Create two users
        # =====================================

        self.user_one = User.objects.create_user(
            username="apiuserone",
            password="TestPassword123!",
        )

        self.user_two = User.objects.create_user(
            username="apiusertwo",
            password="TestPassword123!",
        )

        # =====================================
        # Get automatically created credentials
        # =====================================

        self.credential_one = APIClientCredential.objects.get(user=self.user_one)

        self.credential_two = APIClientCredential.objects.get(user=self.user_two)

        # =====================================
        # Set known client secrets
        # =====================================

        self.secret_one = "UserOneSecret123!"

        self.secret_two = "UserTwoSecret123!"

        self.credential_one.set_client_secret(self.secret_one)

        self.credential_one.save()

        self.credential_two.set_client_secret(self.secret_two)

        self.credential_two.save()

        # =====================================
        # Create private ToDo data
        # =====================================

        self.user_one_todo = ToDoItem.objects.create(
            title="User One Todo",
            description=("Private todo belonging to User One."),
            owner=self.user_one,
        )

        self.user_two_todo = ToDoItem.objects.create(
            title="User Two Todo",
            description=("Private todo belonging to User Two."),
            owner=self.user_two,
        )

        # =====================================
        # API URLs
        # =====================================

        self.token_url = "/api/token/"

        self.todos_url = "/api/todos/"

    # =====================================
    # Valid credentials
    # =====================================

    def test_valid_credentials_return_access_token(self):

        response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertTrue(response.data["access"])

    def test_valid_credentials_return_bearer_token_type(self):

        response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["token_type"],
            "Bearer",
        )

    # =====================================
    # Invalid credentials
    # =====================================

    def test_invalid_client_id_is_rejected(self):

        response = self.client.post(
            self.token_url,
            {
                "client_id": ("this-client-id-does-not-exist"),
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_client_secret_is_rejected(self):

        response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": ("DefinitelyTheWrongSecret"),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_missing_client_id_is_rejected(self):

        response = self.client.post(
            self.token_url,
            {
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_missing_client_secret_is_rejected(self):

        response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================
    # Inactive credentials
    # =====================================

    def test_inactive_credentials_are_rejected(self):

        self.credential_one.active = False

        self.credential_one.save()

        response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================
    # JWT access to protected API
    # =====================================

    def test_access_token_can_access_todos_api(self):

        token_response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            token_response.status_code,
            status.HTTP_200_OK,
        )

        access_token = token_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=(f"Bearer {access_token}"))

        response = self.client.get(self.todos_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # =====================================
    # User data isolation via JWT
    # =====================================

    def test_jwt_only_returns_correct_users_todos(self):

        # Get JWT for User One
        token_response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            token_response.status_code,
            status.HTTP_200_OK,
        )

        access_token = token_response.data["access"]

        # Authenticate using the JWT
        self.client.credentials(HTTP_AUTHORIZATION=(f"Bearer {access_token}"))

        response = self.client.get(self.todos_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        todo_ids = [todo["id"] for todo in response.data]

        # User One's ToDo is visible
        self.assertIn(
            self.user_one_todo.id,
            todo_ids,
        )

        # User Two's ToDo is NOT visible
        self.assertNotIn(
            self.user_two_todo.id,
            todo_ids,
        )

    def test_user_one_credentials_cannot_access_user_two_todo(self):

        # Get JWT for User One
        token_response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": self.secret_one,
            },
            format="json",
        )

        self.assertEqual(
            token_response.status_code,
            status.HTTP_200_OK,
        )

        access_token = token_response.data["access"]

        # Authenticate as User One
        self.client.credentials(HTTP_AUTHORIZATION=(f"Bearer {access_token}"))

        user_two_todo_url = f"/api/todos/{self.user_two_todo.id}/"

        response = self.client.get(user_two_todo_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =====================================
    # Credential isolation
    # =====================================

    def test_each_users_credentials_produce_different_tokens(self):

        response_one = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_one.client_id,
                "client_secret": self.secret_one,
            },
            format="json",
        )

        response_two = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_two.client_id,
                "client_secret": self.secret_two,
            },
            format="json",
        )

        self.assertEqual(
            response_one.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response_two.status_code,
            status.HTTP_200_OK,
        )

        self.assertNotEqual(
            response_one.data["access"],
            response_two.data["access"],
        )

    def test_user_two_token_only_sees_user_two_todos(self):

        # Get JWT for User Two
        token_response = self.client.post(
            self.token_url,
            {
                "client_id": self.credential_two.client_id,
                "client_secret": self.secret_two,
            },
            format="json",
        )

        self.assertEqual(
            token_response.status_code,
            status.HTTP_200_OK,
        )

        access_token = token_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=(f"Bearer {access_token}"))

        response = self.client.get(self.todos_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        todo_ids = [todo["id"] for todo in response.data]

        self.assertIn(
            self.user_two_todo.id,
            todo_ids,
        )

        self.assertNotIn(
            self.user_one_todo.id,
            todo_ids,
        )
