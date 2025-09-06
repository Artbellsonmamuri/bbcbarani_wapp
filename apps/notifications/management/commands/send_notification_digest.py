from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.services import EmailService

User = get_user_model()


class Command(BaseCommand):
    help = 'Send daily notification digest emails to users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--frequency',
            type=str,
            choices=['daily', 'weekly'],
            default='daily',
            help='Digest frequency'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )

    def handle(self, *args, **options):
        frequency = options['frequency']
        dry_run = options['dry_run']

        # Get users who want digest emails
        preferences = NotificationPreference.objects.filter(
            email_frequency=frequency,
            email_enabled=True
        )

        if frequency == 'daily':
            since = timezone.now() - timedelta(days=1)
        else:  # weekly
            since = timezone.now() - timedelta(days=7)

        email_service = EmailService()
        sent_count = 0

        for preference in preferences:
            user = preference.user

            # Get unread notifications since last digest
            notifications = Notification.objects.filter(
                recipient=user,
                created_at__gte=since,
                is_read=False
            ).order_by('-created_at')

            if notifications.exists():
                if dry_run:
                    self.stdout.write(
                        f"Would send {frequency} digest to {user.email} "
                        f"with {notifications.count()} notifications"
                    )
                else:
                    if email_service.send_digest_email(user, notifications):
                        sent_count += 1
                        self.stdout.write(
                            f"Sent {frequency} digest to {user.email}"
                        )
                    else:
                        self.stderr.write(
                            f"Failed to send digest to {user.email}"
                        )

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {sent_count} {frequency} digest emails'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dry run complete - would send {sent_count} emails'
                )
            )
