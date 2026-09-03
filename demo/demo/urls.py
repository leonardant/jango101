from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
from django.urls import include, path

from my1stapp.auth_views import CustomPasswordChangeView


urlpatterns = [

    path("admin/", admin.site.urls),


    # Login
    path(
        "accounts/login/",
        login_not_required(
            auth_views.LoginView.as_view(
                template_name="registration/login.html"
            )
        ),
        name="login",
    ),


    # Logout
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),


    # Change password
    path(
        "accounts/password-change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),


    # Application URLs
    path("", include("my1stapp.urls")),

]