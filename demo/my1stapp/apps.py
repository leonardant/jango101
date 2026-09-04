from django.apps import AppConfig


class My1stappConfig(AppConfig):
    name = 'my1stapp'
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "My 1st App"

    def ready(self):
        import my1stapp.signals
