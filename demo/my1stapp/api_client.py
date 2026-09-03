import requests

from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken


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
    pass


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

        refresh = RefreshToken.for_user(
            self.user
        )

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

        except requests.exceptions.Timeout:

            raise APIConnectionError(
                "The API request timed out. Please try again."
            )


        except requests.exceptions.ConnectionError:

            raise APIConnectionError(
                "Unable to connect to the API. Please try again later."
            )


        except requests.exceptions.RequestException:

            raise APIConnectionError(
                "An error occurred while communicating with the API."
            )


        # =====================================
        # Handle HTTP response codes
        # =====================================

        if response.status_code == 401:

            raise APIAuthenticationError(
                "API authentication failed."
            )


        if response.status_code == 403:

            raise APIPermissionError(
                "You do not have permission to perform this action."
            )


        if response.status_code == 404:

            raise APINotFoundError(
                "The requested item could not be found."
            )


        if response.status_code == 400:

            try:

                errors = response.json()

            except ValueError:

                errors = None


            if errors:

                raise APIValidationError(
                    str(errors)
                )


            raise APIValidationError(
                "The submitted data was invalid."
            )


        if response.status_code >= 500:

            raise APIServerError(
                "The API encountered a server error. Please try again later."
            )


        # Catch any other unexpected error
        if response.status_code >= 400:

            raise APIClientError(
                f"API request failed with status "
                f"{response.status_code}."
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