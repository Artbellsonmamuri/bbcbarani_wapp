from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    """
    Real-time notifications application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Real-Time Notifications'

    def ready(self):
        """Initialize app when Django starts"""
        try:
            import notifications.signals
        except ImportError:
            pass
