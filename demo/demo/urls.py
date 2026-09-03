from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required, login_required
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [

    # =========================
    # Django Admin
    # =========================

    path("admin/", admin.site.urls),


    # =========================
    # API
    # =========================

    path("api/", include("api.urls")),


    # =========================
    # API Documentation
    # =========================

    path(
        "api/schema/",
        login_required(
        SpectacularAPIView.as_view()
        ),
        name="schema",
    ),

    path(
        "api/docs/",
        login_required(
            SpectacularSwaggerView.as_view(
                url_name="schema"
            )
        ),
        name="swagger-ui",
    ),

    path(
        "api/redoc/",
        login_required(
            SpectacularRedocView.as_view(
                url_name="schema"
            )
        ),
        name="redoc",
    ),


    # =========================
    # Authentication
    # =========================

    path(
        "accounts/login/",
        login_not_required(
            auth_views.LoginView.as_view(
                template_name="registration/login.html"
            )
        ),
        name="login",
    ),

    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "accounts/password-change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),

    path(
        "accounts/password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),


    # =========================
    # Main Application
    # =========================

    path("", include("my1stapp.urls")),

]