from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .services import AnalyticsService

User = get_user_model()


# User authentication tracking
@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    """Track user login"""
    service = AnalyticsService()
    service.track_user_activity(
        user=user,
        activity_type='login',
        description=f"User {user.username} logged in",
        request=request
    )


@receiver(user_logged_out)
def handle_user_logout(sender, request, user, **kwargs):
    """Track user logout"""
    if user:
        service = AnalyticsService()
        service.track_user_activity(
            user=user,
            activity_type='logout',
            description=f"User {user.username} logged out",
            request=request
        )
