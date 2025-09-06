from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationQueue
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """Service for managing notifications"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_notification(self, recipient, title, message, notification_type='info', 
                          sender=None, content_object=None, action_url=None, action_text=None,
                          extra_data=None, expires_at=None, priority='normal'):
        """Create a new notification"""

        try:
            notification = Notification.objects.create(
                recipient=recipient,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                sender=sender,
                content_object=content_object,
                action_url=action_url,
                action_text=action_text,
                extra_data=extra_data or {},
                expires_at=expires_at
            )

            # Handle email sending based on user preferences
            self._handle_email_notification(notification)

            self.logger.info(f"Created notification {notification.id} for user {recipient.username}")
            return notification

        except Exception as e:
            self.logger.error(f"Error creating notification: {str(e)}")
            raise

    def _handle_email_notification(self, notification):
        """Handle email sending for notification"""
        try:
            preferences = notification.recipient.notification_preferences

            if not preferences.should_send_email():
                return

            # Check quiet hours
            if preferences.is_quiet_hours():
                # Queue for later
                self._queue_notification_email(notification)
                return

            # Send immediately
            self._send_email_notification(notification)

        except NotificationPreference.DoesNotExist:
            # Default to sending email for users without preferences
            self._send_email_notification(notification)

    def _send_email_notification(self, notification):
        """Send email for notification"""
        try:
            context = {
                'notification': notification,
                'recipient': notification.recipient,
                'site_name': getattr(settings, 'SITE_NAME', 'Bible Baptist Church'),
            }

            # Render email
            html_message = render_to_string('notifications/email/notification.html', context)
            plain_message = strip_tags(html_message)

            # Send email
            send_mail(
                subject=f"[Church] {notification.title}",
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False,
            )

            # Mark as sent
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])

            self.logger.info(f"Sent email notification {notification.id}")

        except Exception as e:
            self.logger.error(f"Error sending email notification {notification.id}: {str(e)}")

    def _queue_notification_email(self, notification):
        """Queue notification email for later sending"""
        # Calculate when to send (after quiet hours)
        # This is a simplified implementation
        next_send_time = timezone.now() + timezone.timedelta(hours=1)

        # In a real implementation, you'd use Celery or similar
        # For now, just log it
        self.logger.info(f"Queued notification {notification.id} for {next_send_time}")

    def bulk_notify(self, recipients, title, message, **kwargs):
        """Send notifications to multiple recipients"""
        notifications = []

        for recipient in recipients:
            try:
                notification = self.create_notification(
                    recipient=recipient,
                    title=title,
                    message=message,
                    **kwargs
                )
                notifications.append(notification)
            except Exception as e:
                self.logger.error(f"Error notifying {recipient.username}: {str(e)}")

        return notifications

    def notify_admins(self, title, message, **kwargs):
        """Send notification to all admins"""
        admins = User.objects.filter(is_staff=True)
        return self.bulk_notify(admins, title, message, **kwargs)

    def notify_ministry_leads(self, title, message, **kwargs):
        """Send notification to ministry leads"""
        leads = User.objects.filter(role='ministry_lead')
        return self.bulk_notify(leads, title, message, **kwargs)

    def notify_by_role(self, role, title, message, **kwargs):
        """Send notifications to users with specific role"""
        if role == 'all':
            users = User.objects.filter(is_active=True)
        elif role == 'admins':
            users = User.objects.filter(is_staff=True)
        elif role == 'members':
            users = User.objects.filter(is_active=True, is_staff=False)
        elif role == 'ministry_leads':
            users = User.objects.filter(role='ministry_lead')
        else:
            return []

        return self.bulk_notify(users, title, message, **kwargs)

    def cleanup_old_notifications(self, days=30):
        """Clean up old read notifications"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()[0]

        self.logger.info(f"Cleaned up {deleted_count} old notifications")
        return deleted_count


class EmailService:
    """Service for handling email notifications"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def send_digest_email(self, user, notifications):
        """Send digest email with multiple notifications"""
        try:
            context = {
                'user': user,
                'notifications': notifications,
                'site_name': getattr(settings, 'SITE_NAME', 'Bible Baptist Church'),
            }

            html_message = render_to_string('notifications/email/digest.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=f"[Church] Daily Digest - {len(notifications)} updates",
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            self.logger.info(f"Sent digest email to {user.username}")
            return True

        except Exception as e:
            self.logger.error(f"Error sending digest email to {user.username}: {str(e)}")
            return False
