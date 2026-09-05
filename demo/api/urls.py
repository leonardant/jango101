from django.urls import path

from . import views
from .views import (
    ClientCredentialsTokenView,
    ToDoDetailAPIView,
    ToDoListCreateAPIView,
)


app_name = "api"


urlpatterns = [
    # =========================
    # Client Credentials Token
    # =========================
    path(
        "token/",
        ClientCredentialsTokenView.as_view(),
        name="client-token",
    ),
    # =========================
    # API Test Endpoint
    # =========================
    path(
        "whoami/",
        views.WhoAmIView.as_view(),
        name="whoami",
    ),
    # =========================
    # To Do API
    # =========================
    path(
        "todos/",
        ToDoListCreateAPIView.as_view(),
        name="todo-list-create",
    ),
    path(
        "todos/<int:pk>/",
        ToDoDetailAPIView.as_view(),
        name="todo-detail",
    ),
]
