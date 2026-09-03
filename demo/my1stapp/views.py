from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, "my1stapp/home.html", {"a_variable": "Hello World! This is my first Django app."})
        ##HttpResponse("Hello World! This is my first Django app.")    


def todos(request):
    from .models import ToDoItem
    todos = ToDoItem.objects.all()
    return render(request, "my1stapp/todos.html", {"todos": todos})