from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Conecta os receivers definidos em core.signals.
        from core import signals  # noqa: F401
