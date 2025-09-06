from django.apps import AppConfig

class EventsConfig(AppConfig):
    """
    Event calendar and RSVP application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'
    verbose_name = 'Event Calendar And Rsvp'
