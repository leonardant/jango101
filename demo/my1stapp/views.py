from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages

from .forms import ProfileForm

from .api_client import APIClient

# Create your views here.
def home(request):
    return render(request, "my1stapp/home.html", {"a_variable": "Hello World! This is my first Django app."})
        ##HttpResponse("Hello World! This is my first Django app.")    

@login_required
def todos(request):

    api = APIClient(
        request.user
    )

    todos = api.get_todos()

    return render(
        request,
        "my1stapp/todos.html",
        {
            "todos": todos,
        },
    )

##def todos(request):
##    from .models import ToDoItem
##    todos = ToDoItem.objects.all()
##    return render(request, "my1stapp/todos.html", {"todos": todos})

def profile(request):
    return render(
        request,
        "my1stapp/profile.html",
    )

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