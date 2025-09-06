from django.apps import AppConfig


class MediaManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.media_manager'
    verbose_name = 'Media Library Manager'

    def ready(self):
        import apps.media_manager.signals
