from django.apps import AppConfig

class MinistriesConfig(AppConfig):
    """
    Ministry showcases application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ministries'
    verbose_name = 'Ministry Showcases'

    def ready(self):
        """Initialize app when Django starts"""
        try:
            import ministries.signals
        except ImportError:
            pass
