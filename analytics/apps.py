from django.apps import AppConfig

class AnalyticsConfig(AppConfig):
    """
    Site analytics tracking application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Site Analytics Tracking'
