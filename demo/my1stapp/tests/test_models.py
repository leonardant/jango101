from django.contrib.auth import get_user_model
from django.test import TestCase

from my1stapp.models import ToDoItem, UserProfile

User = get_user_model()


class ToDoItemModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="TestPassword123!",
        )

    def test_todo_item_string_representation(self):
        todo = ToDoItem.objects.create(
            title="Buy groceries",
            description="Milk, bread, and eggs",
            owner=self.user,
        )

        self.assertEqual(
            str(todo),
            "Buy groceries",
        )


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profile_user",
            password="TestPassword123!",
        )

    def test_user_profile_string_representation(self):
        profile = UserProfile.objects.get(
            user=self.user,
        )

        self.assertEqual(
            str(profile),
            "profile_user",
        )
