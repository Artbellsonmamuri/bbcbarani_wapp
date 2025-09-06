from django.apps import AppConfig

class PrayerConfig(AppConfig):
    """
    Prayer request system application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prayer'
    verbose_name = 'Prayer Request System'
