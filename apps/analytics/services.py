from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
import logging
from .models import (
    PageView, SiteStatistics, UserActivity, ConversionGoal
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service class for analytics operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_overview_metrics(self, start_date, end_date):
        """Get overview metrics for date range"""

        page_views = PageView.objects.filter(
            timestamp__date__range=(start_date, end_date)
        )

        metrics = {
            'total_views': page_views.count(),
            'unique_visitors': page_views.values('ip_address').distinct().count(),
            'registered_users': page_views.filter(user__isnull=False).values('user').distinct().count(),
            'avg_daily_views': 0,
            'avg_session_duration': 0.0,
            'bounce_rate': 0.0,
        }

        # Calculate daily average
        days_count = (end_date - start_date).days + 1
        if days_count > 0:
            metrics['avg_daily_views'] = metrics['total_views'] / days_count

        # Session metrics (simplified calculation)
        sessions = page_views.values('session_key', 'ip_address').annotate(
            duration=Avg('duration'),
            page_count=Count('id')
        ).filter(duration__isnull=False)

        if sessions.exists():
            metrics['avg_session_duration'] = sessions.aggregate(
                avg_duration=Avg('duration')
            )['avg_duration'] or 0.0

            # Bounce rate (sessions with only 1 page view)
            single_page_sessions = sessions.filter(page_count=1).count()
            total_sessions = sessions.count()
            if total_sessions > 0:
                metrics['bounce_rate'] = (single_page_sessions / total_sessions) * 100

        return metrics

    def get_popular_pages(self, start_date, end_date, limit=10):
        """Get most popular pages for date range"""

        popular_pages = PageView.objects.filter(
            timestamp__date__range=(start_date, end_date)
        ).values('path', 'title').annotate(
            views=Count('id'),
            unique_visitors=Count('ip_address', distinct=True)
        ).order_by('-views')[:limit]

        return list(popular_pages)

    def get_device_breakdown(self, start_date, end_date):
        """Get device type breakdown"""

        device_stats = PageView.objects.filter(
            timestamp__date__range=(start_date, end_date)
        ).values('device_type').annotate(
            count=Count('id')
        ).order_by('-count')

        total_views = sum(item['count'] for item in device_stats)

        # Add percentages
        for item in device_stats:
            if total_views > 0:
                item['percentage'] = (item['count'] / total_views) * 100
            else:
                item['percentage'] = 0

        return list(device_stats)

    def get_traffic_sources(self, start_date, end_date):
        """Analyze traffic sources"""

        page_views = PageView.objects.filter(
            timestamp__date__range=(start_date, end_date)
        )

        total_views = page_views.count()

        # Direct traffic (no referrer)
        direct_traffic = page_views.filter(referer='').count()

        # Referral traffic (with referrer)
        referral_views = page_views.exclude(referer='')

        # Categorize referrers
        search_engines = ['google', 'bing', 'yahoo', 'duckduckgo']
        social_networks = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']

        search_traffic = 0
        social_traffic = 0
        other_referral = 0

        for view in referral_views:
            referrer = view.referer.lower()
            if any(engine in referrer for engine in search_engines):
                search_traffic += 1
            elif any(social in referrer for social in social_networks):
                social_traffic += 1
            else:
                other_referral += 1

        traffic_sources = [
            {
                'source': 'Direct',
                'count': direct_traffic,
                'percentage': (direct_traffic / total_views * 100) if total_views > 0 else 0
            },
            {
                'source': 'Search Engines',
                'count': search_traffic,
                'percentage': (search_traffic / total_views * 100) if total_views > 0 else 0
            },
            {
                'source': 'Social Media',
                'count': social_traffic,
                'percentage': (social_traffic / total_views * 100) if total_views > 0 else 0
            },
            {
                'source': 'Referrals',
                'count': other_referral,
                'percentage': (other_referral / total_views * 100) if total_views > 0 else 0
            }
        ]

        return traffic_sources

    def get_daily_trends(self, start_date, end_date):
        """Get daily traffic trends"""

        daily_stats = PageView.objects.filter(
            timestamp__date__range=(start_date, end_date)
        ).extra(
            select={'day': 'DATE(timestamp)'}
        ).values('day').annotate(
            views=Count('id'),
            unique_visitors=Count('ip_address', distinct=True)
        ).order_by('day')

        # Convert to date objects
        trends = []
        for stat in daily_stats:
            trends.append({
                'date': datetime.strptime(stat['day'], '%Y-%m-%d').date(),
                'views': stat['views'],
                'unique_visitors': stat['unique_visitors']
            })

        return trends

    def track_user_activity(self, user, activity_type, description, 
                          content_object=None, metadata=None, request=None):
        """Track user activity"""

        activity_data = {
            'user': user,
            'activity_type': activity_type,
            'description': description,
            'metadata': metadata or {},
        }

        if content_object:
            activity_data['content_object'] = content_object

        if request:
            activity_data['ip_address'] = request.META.get('REMOTE_ADDR', '')
            activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        activity = UserActivity.objects.create(**activity_data)

        self.logger.info(f"Tracked activity: {user.username} - {activity_type}")

        return activity

    def generate_site_statistics(self, date=None):
        """Generate site statistics for a specific date"""

        if date is None:
            date = timezone.now().date() - timedelta(days=1)  # Previous day

        try:
            stats = SiteStatistics.generate_for_date(date)
            self.logger.info(f"Generated statistics for {date}")
            return stats
        except Exception as e:
            self.logger.error(f"Error generating statistics for {date}: {str(e)}")
            raise

    def cleanup_old_data(self, days_to_keep=90):
        """Clean up old analytics data"""

        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        # Clean up page views
        deleted_views = PageView.objects.filter(timestamp__lt=cutoff_date).count()
        PageView.objects.filter(timestamp__lt=cutoff_date).delete()

        # Clean up user activities
        deleted_activities = UserActivity.objects.filter(timestamp__lt=cutoff_date).count()
        UserActivity.objects.filter(timestamp__lt=cutoff_date).delete()

        self.logger.info(
            f"Cleaned up analytics data older than {days_to_keep} days: "
            f"{deleted_views} page views, {deleted_activities} activities"
        )

        return {
            'page_views': deleted_views,
            'activities': deleted_activities,
        }
