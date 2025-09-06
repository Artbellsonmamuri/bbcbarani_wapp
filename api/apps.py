from django.apps import AppConfig

class ApiConfig(AppConfig):
    """
    Centralized API configuration application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Centralized Api Configuration'
