from django.apps import AppConfig


class CookingConfig(AppConfig):
    name = 'cooking'
    def ready(self):
        import cooking.signal
