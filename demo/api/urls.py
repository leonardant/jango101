from django.contrib.auth.decorators import login_not_required, login_required
from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


urlpatterns = [

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