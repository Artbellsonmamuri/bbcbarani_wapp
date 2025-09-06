from django.apps import AppConfig


class PrayerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prayer'
    verbose_name = 'Prayer Requests'

    def ready(self):
        import apps.prayer.signals
