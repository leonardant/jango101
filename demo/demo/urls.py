from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

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
    auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change.html"
    ),
    name="password_change",
),

path(
    "accounts/password-change/done/",
    auth_views.PasswordChangeDoneView.as_view(
        template_name="registration/password_change_done.html"
    ),
    name="password_change_done",
),

    path("", include("my1stapp.urls")),
]