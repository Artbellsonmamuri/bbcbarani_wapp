from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Event, EventRegistration


@receiver(post_save, sender=Event)
def handle_event_created(sender, instance, created, **kwargs):
    """Handle new event creation"""

    if created:
        # TODO: Send notifications to interested users
        # TODO: Add to calendar systems
        pass


@receiver(post_save, sender=EventRegistration)
def handle_registration_created(sender, instance, created, **kwargs):
    """Handle new event registration"""

    if created:
        # TODO: Send confirmation email
        # TODO: Notify event organizer
        pass


@receiver(pre_save, sender=Event)
def handle_event_status_change(sender, instance, **kwargs):
    """Handle event status changes"""

    if instance.pk:
        try:
            old_event = Event.objects.get(pk=instance.pk)

            # Event cancelled
            if old_event.status != 'cancelled' and instance.status == 'cancelled':
                # TODO: Notify all registered users
                pass

            # Event completed
            if old_event.status != 'completed' and instance.status == 'completed':
                # TODO: Send follow-up emails
                pass

        except Event.DoesNotExist:
            pass
