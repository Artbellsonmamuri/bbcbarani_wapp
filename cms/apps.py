from django.apps import AppConfig

class CmsConfig(AppConfig):
    """
    Core content management application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cms'
    verbose_name = 'Core Content Management'

    def ready(self):
        """Initialize app when Django starts"""
        try:
            import cms.signals
        except ImportError:
            pass
