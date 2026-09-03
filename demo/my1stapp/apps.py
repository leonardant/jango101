from django.apps import AppConfig


class My1stappConfig(AppConfig):
    name = 'my1stapp'
    default_auto_field = "django.db.models.BigAutoField"
    ##name = "my1stapp"
    verbose_name = "My 1st App"
