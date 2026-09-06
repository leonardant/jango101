from django.contrib.auth import get_user_model
from django.test import TestCase
from my1stapp.models import ToDoItem

from api.models import APIClientCredential
from api.serializers import (
    ClientCredentialsSerializer,
    ClientCredentialsTokenResponseSerializer,
    ToDoItemSerializer,
    WhoAmISerializer,
)

User = get_user_model()


class ToDoItemSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="todo_user",
            password="TestPassword123!",
        )

    def test_serializes_todo_item(self):
        todo_item = ToDoItem.objects.create(
            title="Test task",
            description="Test description",
            completed=False,
            owner=self.user,
        )

        serializer = ToDoItemSerializer(todo_item)

        self.assertEqual(
            serializer.data["title"],
            "Test task",
        )

        self.assertEqual(
            serializer.data["description"],
            "Test description",
        )

        self.assertFalse(serializer.data["completed"])

    def test_read_only_fields_cannot_be_modified(self):
        todo_item = ToDoItem.objects.create(
            title="Original task",
            description="Original description",
            completed=False,
            owner=self.user,
        )

        serializer = ToDoItemSerializer(
            todo_item,
            data={
                "title": "Updated task",
                "description": "Updated description",
                "completed": True,
                "id": 999,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        updated_item = serializer.save()

        self.assertEqual(
            updated_item.pk,
            todo_item.pk,
        )

        self.assertEqual(
            updated_item.title,
            "Updated task",
        )


class ClientCredentialsSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="api_user",
            password="TestPassword123!",
        )

        self.credential = APIClientCredential.objects.get(
            user=self.user,
        )

        self.raw_secret = "TestClientSecret123!"

        self.credential.set_client_secret(
            self.raw_secret,
        )

        self.credential.save()

    def test_valid_credentials_are_accepted(self):
        serializer = ClientCredentialsSerializer(
            data={
                "client_id": self.credential.client_id,
                "client_secret": self.raw_secret,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["credential"],
            self.credential,
        )

    def test_invalid_client_id_is_rejected(self):
        serializer = ClientCredentialsSerializer(
            data={
                "client_id": "invalid-client-id",
                "client_secret": self.raw_secret,
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "detail",
            serializer.errors,
        )

    def test_inactive_credential_is_rejected(self):
        self.credential.active = False
        self.credential.save()

        serializer = ClientCredentialsSerializer(
            data={
                "client_id": self.credential.client_id,
                "client_secret": self.raw_secret,
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "detail",
            serializer.errors,
        )

    def test_inactive_user_is_rejected(self):
        self.user.is_active = False
        self.user.save()

        serializer = ClientCredentialsSerializer(
            data={
                "client_id": self.credential.client_id,
                "client_secret": self.raw_secret,
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "detail",
            serializer.errors,
        )

    def test_invalid_client_secret_is_rejected(self):
        serializer = ClientCredentialsSerializer(
            data={
                "client_id": self.credential.client_id,
                "client_secret": "WrongSecret123!",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "detail",
            serializer.errors,
        )


class ClientCredentialsTokenResponseSerializerTests(TestCase):
    def test_valid_token_response(self):
        serializer = ClientCredentialsTokenResponseSerializer(
            data={
                "access": "test-access-token",
                "token_type": "Bearer",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_access_token_is_required(self):
        serializer = ClientCredentialsTokenResponseSerializer(
            data={
                "token_type": "Bearer",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "access",
            serializer.errors,
        )


class WhoAmISerializerTests(TestCase):
    def test_valid_user_data(self):
        serializer = WhoAmISerializer(
            data={
                "id": 1,
                "username": "test_user",
                "email": "test@example.com",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_invalid_email_is_rejected(self):
        serializer = WhoAmISerializer(
            data={
                "id": 1,
                "username": "test_user",
                "email": "not-an-email",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "email",
            serializer.errors,
        )
