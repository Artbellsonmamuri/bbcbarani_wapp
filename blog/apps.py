from django.apps import AppConfig

class BlogConfig(AppConfig):
    """
    Blog system with comments application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Blog System With Comments'

    def ready(self):
        """Initialize app when Django starts"""
        try:
            import blog.signals
        except ImportError:
            pass
