from django.apps import AppConfig

class AccountsConfig(AppConfig):
    """
    User authentication and profiles application configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'User Authentication And Profiles'
