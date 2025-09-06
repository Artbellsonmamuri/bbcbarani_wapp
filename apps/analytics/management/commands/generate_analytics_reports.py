from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from apps.analytics.models import SiteStatistics
from apps.analytics.services import AnalyticsService


class Command(BaseCommand):
    help = 'Generate daily analytics statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Generate stats for specific date (YYYY-MM-DD). Default: yesterday'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='Generate stats for this many days back'
        )

    def handle(self, *args, **options):
        service = AnalyticsService()

        if options['date']:
            # Specific date
            target_date = date.fromisoformat(options['date'])
            try:
                stats = service.generate_site_statistics(target_date)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated statistics for {target_date}'
                    )
                )
            except Exception as e:
                self.stderr.write(f'Error generating stats for {target_date}: {str(e)}')
        else:
            # Multiple days
            end_date = timezone.now().date() - timedelta(days=1)  # Yesterday
            days_back = options['days_back']

            generated = 0
            errors = 0

            for i in range(days_back):
                target_date = end_date - timedelta(days=i)
                try:
                    service.generate_site_statistics(target_date)
                    generated += 1
                    self.stdout.write(f'Generated stats for {target_date}')
                except Exception as e:
                    errors += 1
                    self.stderr.write(f'Error for {target_date}: {str(e)}')

            self.stdout.write(
                self.style.SUCCESS(
                    f'Generated {generated} statistics, {errors} errors'
                )
            )
