import logging

import requests

from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken


# Create a logger for this module
logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """
    Base exception for API client errors.
    """

    pass


class APIAuthenticationError(APIClientError):
    pass


class APIPermissionError(APIClientError):
    pass


class APINotFoundError(APIClientError):
    pass


class APIValidationError(APIClientError):
    def __init__(self, message, errors=None):

        super().__init__(message)

        self.errors = errors or {}


class APIServerError(APIClientError):
    pass


class APIConnectionError(APIClientError):
    pass


class APIClient:
    def __init__(self, user):

        self.user = user

        self.base_url = settings.API_BASE_URL.rstrip("/") + "/"

    # =====================================
    # Authentication
    # =====================================

    def get_access_token(self):

        refresh = RefreshToken.for_user(self.user)

        return str(refresh.access_token)

    # =====================================
    # Request headers
    # =====================================

    def get_headers(self):

        token = self.get_access_token()

        return {
            "Authorization": f"Bearer {token}",
        }

    # =====================================
    # Format API validation errors
    # =====================================

    def format_validation_errors(self, errors):

        if not isinstance(errors, dict):
            return "The submitted information was invalid."

        messages = []

        for field, field_errors in errors.items():
            # Convert field name to something readable
            field_name = field.replace("_", " ").title()

            # Ensure errors are always handled as a list
            if not isinstance(field_errors, list):
                field_errors = [field_errors]

            for error in field_errors:
                messages.append(f"{field_name}: {error}")

        if messages:
            return " ".join(messages)

        return "The submitted information was invalid."

    # =====================================
    # Central API request handler
    # =====================================

    def request(
        self,
        method,
        endpoint,
        **kwargs,
    ):

        url = self.base_url + endpoint.lstrip("/")

        try:
            response = requests.request(
                method,
                url,
                headers=self.get_headers(),
                timeout=10,
                **kwargs,
            )

        except requests.exceptions.Timeout as error:
            logger.error(
                "API request timed out. Method=%s URL=%s Error=%s",
                method,
                url,
                error,
            )

            raise APIConnectionError(
                "The service took too long to respond. Please try again."
            )

        except requests.exceptions.ConnectionError as error:
            logger.error(
                "Unable to connect to API. Method=%s URL=%s Error=%s",
                method,
                url,
                error,
            )

            raise APIConnectionError(
                "Unable to connect to the service. Please try again later."
            )

        except requests.exceptions.RequestException as error:
            logger.exception(
                "Unexpected API communication error. Method=%s URL=%s",
                method,
                url,
            )

            raise APIConnectionError(
                "Unable to communicate with the service. Please try again later."
            )

        # =====================================
        # Handle HTTP response codes
        # =====================================

        if response.status_code == 401:
            logger.warning(
                "API authentication failed. Method=%s URL=%s Status=%s User=%s",
                method,
                url,
                response.status_code,
                self.user.username,
            )

            raise APIAuthenticationError("Authentication with the service failed.")

        if response.status_code == 403:
            logger.warning(
                "API permission denied. Method=%s URL=%s Status=%s User=%s",
                method,
                url,
                response.status_code,
                self.user.username,
            )

            raise APIPermissionError(
                "You do not have permission to perform this action."
            )

        if response.status_code == 404:
            logger.info(
                "API resource not found. Method=%s URL=%s Status=%s",
                method,
                url,
                response.status_code,
            )

            raise APINotFoundError("The requested item could not be found.")

        if response.status_code == 400:
            try:
                errors = response.json()

            except ValueError:
                errors = {}

            logger.warning(
                "API validation error. Method=%s URL=%s Status=%s Response=%s",
                method,
                url,
                response.status_code,
                errors,
            )

            formatted_errors = self.format_validation_errors(errors)

            raise APIValidationError(
                formatted_errors,
                errors=errors,
            )

        if response.status_code >= 500:
            logger.error(
                "API server error. Method=%s URL=%s Status=%s Response=%s",
                method,
                url,
                response.status_code,
                response.text,
            )

            raise APIServerError(
                "The service encountered an error. Please try again later."
            )

        # Catch any other unexpected HTTP error
        if response.status_code >= 400:
            logger.error(
                "Unexpected API HTTP error. Method=%s URL=%s Status=%s Response=%s",
                method,
                url,
                response.status_code,
                response.text,
            )

            raise APIClientError(
                "An unexpected error occurred while communicating with the service."
            )

        return response

    # =====================================
    # To Do API
    # =====================================

    def get_todos(self):

        response = self.request(
            "GET",
            "todos/",
        )

        return response.json()

    def create_todo(
        self,
        title,
        description,
        completed=False,
    ):

        response = self.request(
            "POST",
            "todos/",
            json={
                "title": title,
                "description": description,
                "completed": completed,
            },
        )

        return response.json()

    def get_todo(self, todo_id):

        response = self.request(
            "GET",
            f"todos/{todo_id}/",
        )

        return response.json()

    def update_todo(
        self,
        todo_id,
        **data,
    ):

        response = self.request(
            "PATCH",
            f"todos/{todo_id}/",
            json=data,
        )

        return response.json()

    def delete_todo(self, todo_id):

        self.request(
            "DELETE",
            f"todos/{todo_id}/",
        )

        return True
