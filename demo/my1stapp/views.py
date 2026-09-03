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
# Toggle To Do Item
# =====================================

@login_required
def toggle_todo(request, todo_id):

    if request.method != "POST":

        return redirect(
            "my1stapp:todos"
        )

    api = APIClient(
        request.user
    )

    # Get the current To Do item
    todo = api.get_todo(
        todo_id
    )

    # Reverse the completed status
    new_status = not todo["completed"]

    # PATCH the API
    api.update_todo(
        todo_id,
        completed=new_status,
    )

    if new_status:

        messages.success(
            request,
            "To Do item marked as completed."
        )

    else:

        messages.success(
            request,
            "To Do item marked as incomplete."
        )

    return redirect(
        "my1stapp:todos"
    )

# =====================================
# Edit To Do Item
# =====================================

@login_required
def edit_todo(request, todo_id):

    api = APIClient(request.user)

    # Get the existing item from the API.
    # The API remains responsible for checking ownership.
    todo = api.get_todo(todo_id)

    if request.method == "POST":

        form = ToDoForm(request.POST)

        if form.is_valid():

            api.update_todo(
                todo_id,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                completed=form.cleaned_data["completed"],
            )

            messages.success(
                request,
                "To Do item updated successfully."
            )

            return redirect("my1stapp:todos")

    else:

        # Populate the form with data returned by the API
        form = ToDoForm(
            initial={
                "title": todo["title"],
                "description": todo["description"],
                "completed": todo["completed"],
            }
        )

    return render(
        request,
        "my1stapp/edit_todo.html",
        {
            "form": form,
            "todo": todo,
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