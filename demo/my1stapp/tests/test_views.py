from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from my1stapp.api_client import APIClientError, APIValidationError
from my1stapp.forms import ToDoForm
from my1stapp.models import UserProfile

User = get_user_model()


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="homeuser",
            password="TestPassword123!",
        )

    def test_home_page_loads_successfully(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            reverse("my1stapp:home"),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/home.html",
        )

        self.assertEqual(
            response.context["a_variable"],
            "Hello World! This is my first Django app.",
        )


class TodosViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="todosuser",
            password="TestPassword123!",
        )

        self.url = reverse(
            "my1stapp:todos",
        )

    def test_todos_requires_login(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    @patch("my1stapp.views.APIClient")
    def test_todos_loads_successfully(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todos.return_value = [
            {
                "id": 1,
                "title": "First todo",
                "description": "Test description",
                "completed": False,
            }
        ]

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/todos.html",
        )

        self.assertEqual(
            response.context["todos"][0]["title"],
            "First todo",
        )

        mock_api.get_todos.assert_called_once()

    @patch("my1stapp.views.APIClient")
    def test_todos_handles_api_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todos.side_effect = APIClientError(
            "Unable to load todos.",
        )

        response = self.client.get(
            self.url,
            follow=True,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["todos"],
            [],
        )

        self.assertContains(
            response,
            "Unable to load todos.",
        )


class AddTodoViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="addtodouser",
            password="TestPassword123!",
        )

        self.url = reverse(
            "my1stapp:add_todo",
        )

    def test_add_todo_requires_login(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_add_todo_get_displays_form(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/add_todo.html",
        )

        self.assertIsInstance(
            response.context["form"],
            ToDoForm,
        )

    def test_add_todo_invalid_form_returns_errors(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.post(
            self.url,
            {
                "title": "",
                "description": "Description",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFormError(
            response.context["form"],
            "title",
            "This field is required.",
        )

    @patch("my1stapp.views.APIClient")
    def test_add_todo_creates_item_successfully(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        response = self.client.post(
            self.url,
            {
                "title": "New todo",
                "description": "New description",
                "completed": "on",
            },
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        mock_api.create_todo.assert_called_once_with(
            title="New todo",
            description="New description",
            completed=True,
        )

        self.assertContains(
            response,
            "To Do item created successfully.",
        )

    @patch("my1stapp.views.APIClient")
    def test_add_todo_handles_api_validation_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.create_todo.side_effect = APIValidationError(
            "Validation failed.",
            errors={
                "title": [
                    "Title is already in use.",
                ],
            },
        )

        response = self.client.post(
            self.url,
            {
                "title": "Duplicate title",
                "description": "Description",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFormError(
            response.context["form"],
            "title",
            "Title is already in use.",
        )

    @patch("my1stapp.views.APIClient")
    def test_add_todo_handles_api_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.create_todo.side_effect = APIClientError(
            "Unable to create todo.",
        )

        response = self.client.post(
            self.url,
            {
                "title": "New todo",
                "description": "Description",
            },
            follow=True,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Unable to create todo.",
        )


class ToggleTodoViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="toggleuser",
            password="TestPassword123!",
        )

        self.url = reverse(
            "my1stapp:toggle_todo",
            args=[1],
        )

    def test_toggle_todo_requires_login(self):
        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_toggle_todo_get_redirects_to_todos(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            self.url,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

    @patch("my1stapp.views.APIClient")
    def test_toggle_todo_marks_incomplete_item_completed(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.return_value = {
            "id": 1,
            "completed": False,
        }

        response = self.client.post(
            self.url,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        mock_api.update_todo.assert_called_once_with(
            1,
            completed=True,
        )

        self.assertContains(
            response,
            "To Do item marked as completed.",
        )

    @patch("my1stapp.views.APIClient")
    def test_toggle_todo_marks_completed_item_incomplete(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.return_value = {
            "id": 1,
            "completed": True,
        }

        response = self.client.post(
            self.url,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        mock_api.update_todo.assert_called_once_with(
            1,
            completed=False,
        )

        self.assertContains(
            response,
            "To Do item marked as incomplete.",
        )

    @patch("my1stapp.views.APIClient")
    def test_toggle_todo_handles_api_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.side_effect = APIClientError(
            "Unable to update todo.",
        )

        response = self.client.post(
            self.url,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        self.assertContains(
            response,
            "Unable to update todo.",
        )


class EditTodoViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="edituser",
            password="TestPassword123!",
        )

        self.todo_id = 1

        self.url = reverse(
            "my1stapp:edit_todo",
            args=[self.todo_id],
        )

        self.todo = {
            "id": self.todo_id,
            "title": "Existing todo",
            "description": "Existing description",
            "completed": False,
        }

    def test_edit_todo_requires_login(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    @patch("my1stapp.views.APIClient")
    def test_edit_todo_get_displays_existing_values(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.return_value = self.todo

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/edit_todo.html",
        )

        self.assertEqual(
            response.context["form"].initial["title"],
            "Existing todo",
        )

        self.assertEqual(
            response.context["form"].initial["description"],
            "Existing description",
        )

        self.assertFalse(
            response.context["form"].initial["completed"],
        )

    @patch("my1stapp.views.APIClient")
    def test_edit_todo_handles_get_api_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.side_effect = APIClientError(
            "Todo not found.",
        )

        response = self.client.get(
            self.url,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        self.assertContains(
            response,
            "Todo not found.",
        )

    @patch("my1stapp.views.APIClient")
    def test_edit_todo_updates_successfully(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.return_value = self.todo

        response = self.client.post(
            self.url,
            {
                "title": "Updated todo",
                "description": "Updated description",
                "completed": "on",
            },
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        mock_api.update_todo.assert_called_once_with(
            self.todo_id,
            title="Updated todo",
            description="Updated description",
            completed=True,
        )

        self.assertContains(
            response,
            "To Do item updated successfully.",
        )

    @patch("my1stapp.views.APIClient")
    def test_edit_todo_invalid_form_does_not_update_todo(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.return_value = self.todo

        response = self.client.post(
            self.url,
            {
                "description": "Updated description",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/edit_todo.html",
        )

        self.assertFormError(
            response.context["form"],
            "title",
            "This field is required.",
        )

        mock_api.update_todo.assert_not_called()

    @patch("my1stapp.views.APIClient")
    def test_edit_todo_handles_validation_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.return_value = self.todo

        mock_api.update_todo.side_effect = APIValidationError(
            "Validation failed.",
            errors={
                "description": [
                    "Description is invalid.",
                ],
            },
        )

        response = self.client.post(
            self.url,
            {
                "title": "Updated todo",
                "description": "Bad description",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFormError(
            response.context["form"],
            "description",
            "Description is invalid.",
        )

    @patch("my1stapp.views.APIClient")
    def test_edit_todo_handles_api_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.get_todo.return_value = self.todo

        mock_api.update_todo.side_effect = APIClientError(
            "Unable to update todo.",
        )

        response = self.client.post(
            self.url,
            {
                "title": "Updated todo",
                "description": "Updated description",
            },
            follow=True,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Unable to update todo.",
        )


class DeleteTodoViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="deleteuser",
            password="TestPassword123!",
        )

        self.url = reverse(
            "my1stapp:delete_todo",
            args=[1],
        )

    def test_delete_todo_requires_login(self):
        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_delete_todo_get_redirects_to_todos(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            self.url,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

    @patch("my1stapp.views.APIClient")
    def test_delete_todo_succeeds(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        response = self.client.post(
            self.url,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        mock_api_client.return_value.delete_todo.assert_called_once_with(
            1,
        )

        self.assertContains(
            response,
            "To Do item deleted successfully.",
        )

    @patch("my1stapp.views.APIClient")
    def test_delete_todo_handles_api_error(
        self,
        mock_api_client,
    ):
        self.client.force_login(
            self.user,
        )

        mock_api = mock_api_client.return_value

        mock_api.delete_todo.side_effect = APIClientError(
            "Unable to delete todo.",
        )

        response = self.client.post(
            self.url,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse("my1stapp:todos"),
        )

        self.assertContains(
            response,
            "Unable to delete todo.",
        )


class APIErrorHandlingTests(TestCase):
    def test_add_api_errors_to_form_adds_field_errors(self):
        from my1stapp.views import add_api_errors_to_form

        form = ToDoForm(
            data={
                "title": "Test todo",
                "description": "Description",
            }
        )

        self.assertTrue(
            form.is_valid(),
        )

        add_api_errors_to_form(
            form,
            {
                "title": [
                    "First error",
                    "Second error",
                ],
            },
        )

        self.assertIn(
            "First error",
            form.errors["title"],
        )

        self.assertIn(
            "Second error",
            form.errors["title"],
        )

    def test_add_api_errors_to_form_handles_single_error_value(self):
        from my1stapp.views import add_api_errors_to_form

        form = ToDoForm(
            data={
                "title": "Test todo",
                "description": "Description",
            }
        )

        self.assertTrue(
            form.is_valid(),
        )

        add_api_errors_to_form(
            form,
            {
                "title": "Single error",
            },
        )

        self.assertIn(
            "Single error",
            form.errors["title"],
        )

    def test_add_api_errors_to_form_adds_non_field_errors(self):
        from my1stapp.views import add_api_errors_to_form

        form = ToDoForm(
            data={
                "title": "Test todo",
                "description": "Description",
            }
        )

        self.assertTrue(
            form.is_valid(),
        )

        add_api_errors_to_form(
            form,
            {
                "non_field_errors": [
                    "The submitted data is invalid.",
                ],
            },
        )

        self.assertIn(
            "The submitted data is invalid.",
            form.non_field_errors(),
        )

    def test_add_api_errors_to_form_ignores_unknown_fields(self):
        from my1stapp.views import add_api_errors_to_form

        form = ToDoForm(
            data={
                "title": "Test todo",
                "description": "Description",
            }
        )

        self.assertTrue(
            form.is_valid(),
        )

        add_api_errors_to_form(
            form,
            {
                "unknown_field": [
                    "Unknown error",
                ],
            },
        )

        self.assertEqual(
            form.errors,
            {},
        )


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            password="TestPassword123!",
        )

        self.profile_url = reverse(
            "my1stapp:profile",
        )

        self.edit_profile_url = reverse(
            "my1stapp:edit_profile",
        )

    def test_profile_requires_login(self):
        response = self.client.get(
            self.profile_url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_profile_loads_successfully(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            self.profile_url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/profile.html",
        )

    def test_edit_profile_get_displays_form(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            self.edit_profile_url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/edit_profile.html",
        )

        self.assertEqual(
            response.context["form"].instance,
            self.user,
        )

    def test_edit_profile_updates_user(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.post(
            self.edit_profile_url,
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
            },
            follow=True,
        )

        self.assertRedirects(
            response,
            self.profile_url,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Jane",
        )

        self.assertEqual(
            self.user.last_name,
            "Smith",
        )

        self.assertEqual(
            self.user.email,
            "jane@example.com",
        )

        self.assertContains(
            response,
            "Your profile was updated successfully.",
        )

    def test_edit_profile_invalid_data_returns_form(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.post(
            self.edit_profile_url,
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "not-a-valid-email",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFormError(
            response.context["form"],
            "email",
            "Enter a valid email address.",
        )


class LanguageSettingsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="languageuser",
            password="TestPassword123!",
        )

        self.url = reverse(
            "my1stapp:language_settings",
        )

    def test_language_settings_requires_login(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_language_settings_get_displays_form(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "my1stapp/language_settings.html",
        )

        self.assertEqual(
            response.context["form"].instance.language,
            "en-gb",
        )

    def test_language_settings_updates_language(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.post(
            self.url,
            {
                "language": "fr",
            },
        )

        self.assertRedirects(
            response,
            self.url,
        )

        profile = UserProfile.objects.get(
            user=self.user,
        )

        self.assertEqual(
            profile.language,
            "fr",
        )

    def test_language_settings_invalid_data_returns_form(self):
        self.client.force_login(
            self.user,
        )

        response = self.client.post(
            self.url,
            {
                "language": "invalid-language",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFormError(
            response.context["form"],
            "language",
            (
                "Select a valid choice. invalid-language is not one "
                "of the available choices."
            ),
        )
