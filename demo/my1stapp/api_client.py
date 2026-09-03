import requests

from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken


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
    # To Do API
    # =====================================

    def get_todos(self):

        response = requests.get(
            self.base_url + "todos/",
            headers=self.get_headers(),
        )

        response.raise_for_status()

        return response.json()


    def create_todo(
        self,
        title,
        description,
        completed=False,
    ):

        response = requests.post(
            self.base_url + "todos/",
            headers=self.get_headers(),
            json={
                "title": title,
                "description": description,
                "completed": completed,
            },
        )

        response.raise_for_status()

        return response.json()


    def get_todo(self, todo_id):

        response = requests.get(
            self.base_url + f"todos/{todo_id}/",
            headers=self.get_headers(),
        )

        response.raise_for_status()

        return response.json()


    def update_todo(
        self,
        todo_id,
        **data,
    ):

        response = requests.patch(
            self.base_url + f"todos/{todo_id}/",
            headers=self.get_headers(),
            json=data,
        )

        response.raise_for_status()

        return response.json()


    def delete_todo(self, todo_id):

        response = requests.delete(
            self.base_url + f"todos/{todo_id}/",
            headers=self.get_headers(),
        )

        response.raise_for_status()

        return response.status_code == 204