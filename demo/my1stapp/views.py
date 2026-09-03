from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ProfileForm, ToDoForm
from .api_client import APIClient


# =====================================
# Home
# =====================================

def home(request):

    return render(
        request,
        "my1stapp/home.html",
        {
            "a_variable": "Hello World! This is my first Django app.",
        },
    )


# =====================================
# To Do List
# =====================================

@login_required
def todos(request):

    api = APIClient(request.user)

    todos = api.get_todos()

    return render(
        request,
        "my1stapp/todos.html",
        {
            "todos": todos,
        },
    )


# =====================================
# Add To Do Item
# =====================================

@login_required
def add_todo(request):

    if request.method == "POST":

        form = ToDoForm(request.POST)

        if form.is_valid():

            api = APIClient(request.user)

            api.create_todo(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                completed=form.cleaned_data["completed"],
            )

            messages.success(
                request,
                "To Do item created successfully."
            )

            return redirect(
                "my1stapp:todos"
            )

    else:

        form = ToDoForm()

    return render(
        request,
        "my1stapp/add_todo.html",
        {
            "form": form,
        },
    )


# =====================================
# Profile
# =====================================

@login_required
def profile(request):

    return render(
        request,
        "my1stapp/profile.html",
    )


# =====================================
# Edit Profile
# =====================================

@login_required
def edit_profile(request):

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            instance=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Your profile was updated successfully."
            )

            return redirect("my1stapp:profile")

    else:

        form = ProfileForm(
            instance=request.user
        )

    return render(
        request,
        "my1stapp/edit_profile.html",
        {
            "form": form,
        },
    )