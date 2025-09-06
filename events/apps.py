from django.apps import AppConfig

class EventsConfig(AppConfig):
    """
    Event calendar and RSVP application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'
    verbose_name = 'Event Calendar And Rsvp'

    def ready(self):
        """Initialize app when Django starts"""
        try:
            import events.signals
        except ImportError:
            pass
