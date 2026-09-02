from django.shortcuts import render, HttpResponse

# Create your views here.
def home(request):
    return render(request, "home.html", {"a_variable": "Hello World! This is my first Django app."})
        ##HttpResponse("Hello World! This is my first Django app.")    