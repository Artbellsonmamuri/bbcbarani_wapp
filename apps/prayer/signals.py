from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PrayerRequest

User = get_user_model()


@receiver(post_save, sender=PrayerRequest)
def notify_prayer_team(sender, instance, created, **kwargs):
    """Send notifications when new prayer requests are submitted"""

    if created:
        # TODO: Implement notification system
        # This could send emails to prayer team members
        # or create notifications in the notification app
        pass


@receiver(post_save, sender=PrayerRequest)
def update_status_timestamps(sender, instance, **kwargs):
    """Update timestamp fields when status changes"""

    from django.utils import timezone

    if instance.status == 'reviewing' and not instance.reviewed_at:
        PrayerRequest.objects.filter(pk=instance.pk).update(reviewed_at=timezone.now())
    elif instance.status == 'answered' and not instance.answered_at:
        PrayerRequest.objects.filter(pk=instance.pk).update(answered_at=timezone.now())
