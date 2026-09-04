from django.apps import AppConfig


class My1stappConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "my1stapp"

    verbose_name = "My 1st App"

    def ready(self):

        import my1stapp.signals