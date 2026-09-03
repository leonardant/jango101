from django.urls import path
from . import views

app_name = "my1stapp"

urlpatterns = [
    path("", views.home, name='home'),
    path("todos/", views.todos, name='todos'),
    path("todos/add/", views.add_todo, name="add_todo"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
]