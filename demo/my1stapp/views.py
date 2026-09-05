from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .api_client import APIClient, APIClientError, APIValidationError
from .forms import LanguageForm, ProfileForm, ToDoForm

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

    try:
        todos = api.get_todos()

    except APIClientError as error:
        messages.error(
            request,
            str(error),
        )

        todos = []

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

            try:
                api.create_todo(
                    title=form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    completed=form.cleaned_data["completed"],
                )

            except APIValidationError as error:
                add_api_errors_to_form(
                    form,
                    error.errors,
                )

            except APIClientError as error:
                messages.error(
                    request,
                    str(error),
                )

            else:
                messages.success(request, "To Do item created successfully.")

                return redirect("my1stapp:todos")

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
        return redirect("my1stapp:todos")

    api = APIClient(request.user)

    try:
        todo = api.get_todo(todo_id)

        new_status = not todo["completed"]

        api.update_todo(
            todo_id,
            completed=new_status,
        )

    except APIClientError as error:
        messages.error(
            request,
            str(error),
        )

        return redirect("my1stapp:todos")

    if new_status:
        messages.success(request, "To Do item marked as completed.")

    else:
        messages.success(request, "To Do item marked as incomplete.")

    return redirect("my1stapp:todos")


# =====================================
# Edit To Do Item
# =====================================


@login_required
def edit_todo(request, todo_id):

    api = APIClient(request.user)

    try:
        todo = api.get_todo(todo_id)

    except APIClientError as error:
        messages.error(
            request,
            str(error),
        )

        return redirect("my1stapp:todos")

    if request.method == "POST":
        form = ToDoForm(request.POST)

        if form.is_valid():
            try:
                api.update_todo(
                    todo_id,
                    title=form.cleaned_data["title"],
                    description=form.cleaned_data["description"],
                    completed=form.cleaned_data["completed"],
                )

            except APIValidationError as error:
                add_api_errors_to_form(
                    form,
                    error.errors,
                )

            except APIClientError as error:
                messages.error(
                    request,
                    str(error),
                )

            else:
                messages.success(request, "To Do item updated successfully.")

                return redirect("my1stapp:todos")

    else:
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
# Delete To Do Item
# =====================================


@login_required
def delete_todo(request, todo_id):

    if request.method != "POST":
        return redirect("my1stapp:todos")

    api = APIClient(request.user)

    try:
        api.delete_todo(todo_id)

    except APIClientError as error:
        messages.error(
            request,
            str(error),
        )

    else:
        messages.success(request, "To Do item deleted successfully.")

    return redirect("my1stapp:todos")


# =====================================
# API ERROR HANDLING
# =====================================
def add_api_errors_to_form(form, api_errors):

    for field, errors in api_errors.items():
        # DRF may return non-field errors
        if field == "non_field_errors":
            for error in errors:
                form.add_error(
                    None,
                    error,
                )

            continue

        # Only add errors to fields that exist on this form
        if field in form.fields:
            if not isinstance(errors, list):
                errors = [errors]

            for error in errors:
                form.add_error(
                    field,
                    error,
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

            messages.success(request, "Your profile was updated successfully.")

            return redirect("my1stapp:profile")

    else:
        form = ProfileForm(instance=request.user)

    return render(
        request,
        "my1stapp/edit_profile.html",
        {
            "form": form,
        },
    )


@login_required
def language_settings(request):

    profile, _created = request.user.profile.__class__.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = LanguageForm(
            request.POST,
            instance=profile,
        )

        if form.is_valid():
            form.save()

            return redirect("my1stapp:language_settings")

    else:
        form = LanguageForm(instance=profile)

    return render(
        request,
        "my1stapp/language_settings.html",
        {
            "form": form,
        },
    )
