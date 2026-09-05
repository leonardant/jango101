from unittest.mock import Mock, patch

import requests

from django.contrib.auth import get_user_model
from django.test import TestCase

from my1stapp.api_client import (
    APIAuthenticationError,
    APIClient,
    APIClientError,
    APIConnectionError,
    APINotFoundError,
    APIPermissionError,
    APIServerError,
    APIValidationError,
)


User = get_user_model()


class APIClientTests(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="api_client_test_user",
            password="TestPassword123!",
        )

        self.api_client = APIClient(self.user)

    # =====================================
    # Authentication and headers
    # =====================================

    def test_get_access_token_returns_token(self):

        token = self.api_client.get_access_token()

        self.assertIsInstance(
            token,
            str,
        )

        self.assertTrue(token)

    def test_get_headers_returns_bearer_token(self):

        headers = self.api_client.get_headers()

        self.assertIn(
            "Authorization",
            headers,
        )

        self.assertTrue(headers["Authorization"].startswith("Bearer "))

    # =====================================
    # Successful requests
    # =====================================

    @patch("my1stapp.api_client.requests.request")
    def test_successful_request_returns_response(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 200

        mock_request.return_value = response

        result = self.api_client.request(
            "GET",
            "todos/",
        )

        self.assertIs(
            result,
            response,
        )

    @patch("my1stapp.api_client.requests.request")
    def test_request_builds_correct_url(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 200

        mock_request.return_value = response

        self.api_client.request(
            "GET",
            "/todos/",
        )

        mock_request.assert_called_once()

        args, kwargs = mock_request.call_args

        self.assertEqual(
            args[0],
            "GET",
        )

        self.assertEqual(
            args[1],
            "http://127.0.0.1:8000/api/todos/",
        )

    @patch("my1stapp.api_client.requests.request")
    def test_request_uses_timeout(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 200

        mock_request.return_value = response

        self.api_client.request(
            "GET",
            "todos/",
        )

        args, kwargs = mock_request.call_args

        self.assertEqual(
            kwargs["timeout"],
            10,
        )

    # =====================================
    # Connection errors
    # =====================================

    @patch("my1stapp.api_client.requests.request")
    def test_timeout_raises_api_connection_error(
        self,
        mock_request,
    ):

        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

        with self.assertRaises(APIConnectionError) as context:
            self.api_client.request(
                "GET",
                "todos/",
            )

        self.assertEqual(
            str(context.exception),
            ("The service took too long to respond. Please try again."),
        )

    @patch("my1stapp.api_client.requests.request")
    def test_connection_error_raises_api_connection_error(
        self,
        mock_request,
    ):

        mock_request.side_effect = requests.exceptions.ConnectionError(
            "Unable to connect"
        )

        with self.assertRaises(APIConnectionError) as context:
            self.api_client.request(
                "GET",
                "todos/",
            )

        self.assertEqual(
            str(context.exception),
            ("Unable to connect to the service. Please try again later."),
        )

    @patch("my1stapp.api_client.requests.request")
    def test_unexpected_request_error_raises_api_connection_error(
        self,
        mock_request,
    ):

        mock_request.side_effect = requests.exceptions.RequestException(
            "Unexpected request error"
        )

        with self.assertRaises(APIConnectionError) as context:
            self.api_client.request(
                "GET",
                "todos/",
            )

        self.assertEqual(
            str(context.exception),
            ("Unable to communicate with the service. Please try again later."),
        )

    # =====================================
    # HTTP authentication errors
    # =====================================

    @patch("my1stapp.api_client.requests.request")
    def test_401_raises_api_authentication_error(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 401

        mock_request.return_value = response

        with self.assertRaises(APIAuthenticationError):
            self.api_client.request(
                "GET",
                "todos/",
            )

    @patch("my1stapp.api_client.requests.request")
    def test_403_raises_api_permission_error(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 403

        mock_request.return_value = response

        with self.assertRaises(APIPermissionError):
            self.api_client.request(
                "GET",
                "todos/",
            )

    @patch("my1stapp.api_client.requests.request")
    def test_404_raises_api_not_found_error(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 404

        mock_request.return_value = response

        with self.assertRaises(APINotFoundError):
            self.api_client.request(
                "GET",
                "todos/",
            )

    # =====================================
    # Validation errors
    # =====================================

    @patch("my1stapp.api_client.requests.request")
    def test_400_raises_api_validation_error(
        self,
        mock_request,
    ):

        errors = {
            "title": ["This field is required."],
        }

        response = Mock()

        response.status_code = 400

        response.json.return_value = errors

        mock_request.return_value = response

        with self.assertRaises(APIValidationError) as context:
            self.api_client.request(
                "POST",
                "todos/",
            )

        exception = context.exception

        self.assertEqual(
            exception.errors,
            errors,
        )

        self.assertEqual(
            str(exception),
            ("Title: This field is required."),
        )

    @patch("my1stapp.api_client.requests.request")
    def test_400_with_invalid_json_returns_generic_error(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 400

        response.json.side_effect = ValueError("Invalid JSON")

        mock_request.return_value = response

        with self.assertRaises(APIValidationError) as context:
            self.api_client.request(
                "POST",
                "todos/",
            )

        self.assertEqual(
            context.exception.errors,
            {},
        )

        self.assertEqual(
            str(context.exception),
            "The submitted information was invalid.",
        )

    # =====================================
    # Server errors
    # =====================================

    @patch("my1stapp.api_client.requests.request")
    def test_500_raises_api_server_error(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 500

        response.text = "Internal Server Error"

        mock_request.return_value = response

        with self.assertRaises(APIServerError):
            self.api_client.request(
                "GET",
                "todos/",
            )

    @patch("my1stapp.api_client.requests.request")
    def test_503_raises_api_server_error(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 503

        response.text = "Service Unavailable"

        mock_request.return_value = response

        with self.assertRaises(APIServerError):
            self.api_client.request(
                "GET",
                "todos/",
            )

    # =====================================
    # Unexpected HTTP errors
    # =====================================

    @patch("my1stapp.api_client.requests.request")
    def test_unexpected_4xx_error_raises_api_client_error(
        self,
        mock_request,
    ):

        response = Mock()

        response.status_code = 429

        response.text = "Too Many Requests"

        mock_request.return_value = response

        with self.assertRaises(APIClientError):
            self.api_client.request(
                "GET",
                "todos/",
            )

    # =====================================
    # Validation error formatting
    # =====================================

    def test_format_validation_errors_formats_multiple_fields(
        self,
    ):

        errors = {
            "title": ["This field is required."],
            "description": ["This field is required."],
        }

        result = self.api_client.format_validation_errors(errors)

        self.assertEqual(
            result,
            ("Title: This field is required. Description: This field is required."),
        )

    def test_format_validation_errors_formats_single_error_value(
        self,
    ):

        errors = {
            "title": "This field is required.",
        }

        result = self.api_client.format_validation_errors(errors)

        self.assertEqual(
            result,
            "Title: This field is required.",
        )

    def test_format_validation_errors_handles_non_dictionary(
        self,
    ):

        result = self.api_client.format_validation_errors(["Invalid data"])

        self.assertEqual(
            result,
            "The submitted information was invalid.",
        )

    def test_format_validation_errors_handles_empty_dictionary(
        self,
    ):

        result = self.api_client.format_validation_errors({})

        self.assertEqual(
            result,
            "The submitted information was invalid.",
        )

    # =====================================
    # To Do API convenience methods
    # =====================================

    @patch.object(APIClient, "request")
    def test_get_todos_returns_json(
        self,
        mock_request,
    ):

        response = Mock()

        response.json.return_value = [
            {
                "id": 1,
                "title": "Test Todo",
            }
        ]

        mock_request.return_value = response

        result = self.api_client.get_todos()

        self.assertEqual(
            result,
            [
                {
                    "id": 1,
                    "title": "Test Todo",
                }
            ],
        )

        mock_request.assert_called_once_with(
            "GET",
            "todos/",
        )

    @patch.object(APIClient, "request")
    def test_create_todo_sends_correct_data(
        self,
        mock_request,
    ):

        response = Mock()

        response.json.return_value = {
            "id": 1,
            "title": "New Todo",
            "description": "Test description",
            "completed": False,
        }

        mock_request.return_value = response

        result = self.api_client.create_todo(
            title="New Todo",
            description="Test description",
        )

        self.assertEqual(
            result["title"],
            "New Todo",
        )

        mock_request.assert_called_once_with(
            "POST",
            "todos/",
            json={
                "title": "New Todo",
                "description": "Test description",
                "completed": False,
            },
        )

    @patch.object(APIClient, "request")
    def test_create_todo_can_set_completed(
        self,
        mock_request,
    ):

        response = Mock()

        response.json.return_value = {
            "id": 1,
            "completed": True,
        }

        mock_request.return_value = response

        self.api_client.create_todo(
            title="Completed Todo",
            description="Already completed",
            completed=True,
        )

        mock_request.assert_called_once_with(
            "POST",
            "todos/",
            json={
                "title": "Completed Todo",
                "description": "Already completed",
                "completed": True,
            },
        )

    @patch.object(APIClient, "request")
    def test_get_todo_returns_json(
        self,
        mock_request,
    ):

        response = Mock()

        response.json.return_value = {
            "id": 5,
            "title": "Test Todo",
        }

        mock_request.return_value = response

        result = self.api_client.get_todo(5)

        self.assertEqual(
            result["id"],
            5,
        )

        mock_request.assert_called_once_with(
            "GET",
            "todos/5/",
        )

    @patch.object(APIClient, "request")
    def test_update_todo_sends_correct_data(
        self,
        mock_request,
    ):

        response = Mock()

        response.json.return_value = {
            "id": 5,
            "title": "Updated Todo",
        }

        mock_request.return_value = response

        result = self.api_client.update_todo(
            5,
            title="Updated Todo",
            completed=True,
        )

        self.assertEqual(
            result["title"],
            "Updated Todo",
        )

        mock_request.assert_called_once_with(
            "PATCH",
            "todos/5/",
            json={
                "title": "Updated Todo",
                "completed": True,
            },
        )

    @patch.object(APIClient, "request")
    def test_delete_todo_returns_true(
        self,
        mock_request,
    ):

        result = self.api_client.delete_todo(5)

        self.assertTrue(result)

        mock_request.assert_called_once_with(
            "DELETE",
            "todos/5/",
        )
