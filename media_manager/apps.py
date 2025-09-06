from django.apps import AppConfig

class MediamanagerConfig(AppConfig):
    """
    Media library management application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media_manager'
    verbose_name = 'Media Library Management'

    def ready(self):
        """Initialize app when Django starts"""
        try:
            import media_manager.signals
        except ImportError:
            pass
