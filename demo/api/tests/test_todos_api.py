from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from my1stapp.models import ToDoItem


User = get_user_model()


class ToDoAPISecurityTests(APITestCase):

    def setUp(self):

        self.user_one = User.objects.create_user(
            username="userone",
            password="TestPassword123!",
        )

        self.user_two = User.objects.create_user(
            username="usertwo",
            password="TestPassword123!",
        )

        self.user_one_todo = ToDoItem.objects.create(
            title="User One Private Todo",
            description="This belongs to User One.",
            owner=self.user_one,
        )

        self.user_two_todo = ToDoItem.objects.create(
            title="User Two Private Todo",
            description="This belongs to User Two.",
            owner=self.user_two,
        )

        self.todos_url = "/api/todos/"


    # =====================================
    # Authentication tests
    # =====================================

    def test_unauthenticated_user_cannot_list_todos(self):

        response = self.client.get(
            self.todos_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_unauthenticated_user_cannot_create_todo(self):

        response = self.client.post(
            self.todos_url,
            {
                "title": "Unauthorized Todo",
                "description": "Should not be created.",
                "completed": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            ToDoItem.objects.filter(
                title="Unauthorized Todo",
            ).exists()
        )


    # =====================================
    # List security tests
    # =====================================

    def test_user_only_sees_own_todos(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        response = self.client.get(
            self.todos_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        todo_ids = [
            todo["id"]
            for todo in response.data
        ]

        self.assertIn(
            self.user_one_todo.id,
            todo_ids,
        )

        self.assertNotIn(
            self.user_two_todo.id,
            todo_ids,
        )


    def test_user_does_not_see_other_users_todo_in_list(self):

        self.client.force_authenticate(
            user=self.user_two
        )

        response = self.client.get(
            self.todos_url
        )

        todo_ids = [
            todo["id"]
            for todo in response.data
        ]

        self.assertNotIn(
            self.user_one_todo.id,
            todo_ids,
        )


    # =====================================
    # Create tests
    # =====================================

    def test_authenticated_user_can_create_todo(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        response = self.client.post(
            self.todos_url,
            {
                "title": "New Todo",
                "description": "Created through the API.",
                "completed": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        todo = ToDoItem.objects.get(
            title="New Todo"
        )

        self.assertEqual(
            todo.owner,
            self.user_one,
        )


    def test_user_cannot_choose_another_owner_when_creating_todo(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        response = self.client.post(
            self.todos_url,
            {
                "title": "Attempted Ownership Attack",
                "description": "Trying to assign this todo to another user.",
                "completed": False,
                "owner": self.user_two.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        todo = ToDoItem.objects.get(
            title="Attempted Ownership Attack"
        )

        self.assertEqual(
            todo.owner,
            self.user_one,
        )


    # =====================================
    # Retrieve security tests
    # =====================================

    def test_user_can_retrieve_own_todo(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        url = (
            f"/api/todos/{self.user_one_todo.id}/"
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.user_one_todo.id,
        )


    def test_user_cannot_retrieve_other_users_todo(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        url = (
            f"/api/todos/{self.user_two_todo.id}/"
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


    # =====================================
    # Update security tests
    # =====================================

    def test_user_can_update_own_todo(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        url = (
            f"/api/todos/{self.user_one_todo.id}/"
        )

        response = self.client.patch(
            url,
            {
                "title": "Updated Todo Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user_one_todo.refresh_from_db()

        self.assertEqual(
            self.user_one_todo.title,
            "Updated Todo Title",
        )


    def test_user_cannot_update_other_users_todo(self):

        original_title = self.user_two_todo.title

        self.client.force_authenticate(
            user=self.user_one
        )

        url = (
            f"/api/todos/{self.user_two_todo.id}/"
        )

        response = self.client.patch(
            url,
            {
                "title": "Hacked Todo",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.user_two_todo.refresh_from_db()

        self.assertEqual(
            self.user_two_todo.title,
            original_title,
        )


    # =====================================
    # Delete security tests
    # =====================================

    def test_user_can_delete_own_todo(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        url = (
            f"/api/todos/{self.user_one_todo.id}/"
        )

        response = self.client.delete(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            ToDoItem.objects.filter(
                id=self.user_one_todo.id,
            ).exists()
        )


    def test_user_cannot_delete_other_users_todo(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        url = (
            f"/api/todos/{self.user_two_todo.id}/"
        )

        response = self.client.delete(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            ToDoItem.objects.filter(
                id=self.user_two_todo.id,
            ).exists()
        )


    # =====================================
    # Completed status tests
    # =====================================

    def test_user_can_mark_own_todo_as_completed(self):

        self.client.force_authenticate(
            user=self.user_one
        )

        url = (
            f"/api/todos/{self.user_one_todo.id}/"
        )

        response = self.client.patch(
            url,
            {
                "completed": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user_one_todo.refresh_from_db()

        self.assertTrue(
            self.user_one_todo.completed
        )