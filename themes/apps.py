from django.apps import AppConfig

class ThemesConfig(AppConfig):
    """
    Theme and CSS management application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'themes'
    verbose_name = 'Theme And Css Management'

    def ready(self):
        """Initialize app when Django starts"""
        try:
            import themes.signals
        except ImportError:
            pass
