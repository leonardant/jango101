from django.urls import path

from .views import WhoAmIView


app_name = "api"


urlpatterns = [

    path(
        "whoami/",
        WhoAmIView.as_view(),
        name="whoami",
    ),

]