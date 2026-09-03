from django.contrib.auth.decorators import login_not_required, login_required
from django.urls import path

from .views import (
    ToDoDetailAPIView,
    ToDoListCreateAPIView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

app_name = "api"

urlpatterns = [

    # =========================
    # ToDo API endpoints
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

    # =========================
    # API test endpoint
    # =========================

    path(
        "whoami/",
        views.WhoAmIView.as_view(),
        name="whoami",
    ),


    # =========================
    # JWT Authentication
    # =========================

    path(
        "auth/token/",
        login_not_required(
            TokenObtainPairView.as_view()
        ),
        name="token_obtain_pair",
    ),

    path(
        "auth/token/refresh/",
        login_not_required(
            TokenRefreshView.as_view()
        ),
        name="token_refresh",
    ),

]