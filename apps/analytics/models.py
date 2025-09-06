from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.db.models import Count, Sum, Avg
import json
from datetime import datetime, timedelta

User = get_user_model()


class PageView(models.Model):
    """Track page views and visitor analytics"""

    # Page information
    url = models.URLField()
    path = models.CharField(max_length=500)
    title = models.CharField(max_length=255, blank=True)

    # Visitor information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField()

    # Request information
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    device_type = models.CharField(max_length=20, choices=[
        ('desktop', 'Desktop'),
        ('tablet', 'Tablet'),
        ('mobile', 'Mobile'),
        ('bot', 'Bot'),
        ('unknown', 'Unknown'),
    ], default='unknown')
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)

    # Location information (optional)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Timing information
    timestamp = models.DateTimeField(default=timezone.now)
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Time spent on page in seconds")

    class Meta:
        verbose_name = _('Page View')
        verbose_name_plural = _('Page Views')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['path', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.path} - {self.timestamp}"

    @property
    def is_unique_visitor(self):
        """Check if this is a unique visitor for the day"""
        start_of_day = self.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        previous_views = PageView.objects.filter(
            ip_address=self.ip_address,
            timestamp__range=(start_of_day, end_of_day)
        ).exclude(id=self.id)

        return not previous_views.exists()


class SiteStatistics(models.Model):
    """Daily site statistics summary"""

    date = models.DateField(unique=True)

    # View counts
    total_page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    registered_user_views = models.PositiveIntegerField(default=0)

    # Popular content
    most_viewed_page = models.CharField(max_length=500, blank=True)
    most_viewed_page_views = models.PositiveIntegerField(default=0)

    # Device breakdown
    desktop_views = models.PositiveIntegerField(default=0)
    mobile_views = models.PositiveIntegerField(default=0)
    tablet_views = models.PositiveIntegerField(default=0)

    # Traffic sources
    direct_traffic = models.PositiveIntegerField(default=0)
    search_traffic = models.PositiveIntegerField(default=0)
    social_traffic = models.PositiveIntegerField(default=0)
    referral_traffic = models.PositiveIntegerField(default=0)

    # Engagement metrics
    avg_session_duration = models.FloatField(default=0.0, help_text="Average session duration in minutes")
    bounce_rate = models.FloatField(default=0.0, help_text="Percentage of single-page sessions")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Site Statistics')
        verbose_name_plural = _('Site Statistics')
        ordering = ['-date']

    def __str__(self):
        return f"Stats for {self.date}"

    @classmethod
    def generate_for_date(cls, target_date):
        """Generate statistics for a specific date"""
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)

        # Get page views for the date
        page_views = PageView.objects.filter(
            timestamp__range=(start_datetime, end_datetime)
        )

        # Calculate statistics
        total_views = page_views.count()
        unique_visitors = page_views.values('ip_address').distinct().count()
        registered_views = page_views.filter(user__isnull=False).count()

        # Device breakdown
        device_counts = page_views.values('device_type').annotate(count=Count('id'))
        device_breakdown = {item['device_type']: item['count'] for item in device_counts}

        # Most viewed page
        popular_pages = page_views.values('path').annotate(
            count=Count('id')
        ).order_by('-count').first()

        most_viewed_page = popular_pages['path'] if popular_pages else ''
        most_viewed_count = popular_pages['count'] if popular_pages else 0

        # Traffic sources (simplified)
        referer_analysis = page_views.exclude(referer='').values('referer')
        direct_count = page_views.filter(referer='').count()
        search_count = sum(1 for r in referer_analysis if any(search in r['referer'] for search in ['google', 'bing', 'yahoo']))
        social_count = sum(1 for r in referer_analysis if any(social in r['referer'] for social in ['facebook', 'twitter', 'instagram']))
        referral_count = total_views - direct_count - search_count - social_count

        # Create or update statistics
        stats, created = cls.objects.get_or_create(
            date=target_date,
            defaults={
                'total_page_views': total_views,
                'unique_visitors': unique_visitors,
                'registered_user_views': registered_views,
                'most_viewed_page': most_viewed_page,
                'most_viewed_page_views': most_viewed_count,
                'desktop_views': device_breakdown.get('desktop', 0),
                'mobile_views': device_breakdown.get('mobile', 0),
                'tablet_views': device_breakdown.get('tablet', 0),
                'direct_traffic': direct_count,
                'search_traffic': search_count,
                'social_traffic': social_count,
                'referral_traffic': referral_count,
            }
        )

        if not created:
            # Update existing record
            stats.total_page_views = total_views
            stats.unique_visitors = unique_visitors
            stats.registered_user_views = registered_views
            stats.most_viewed_page = most_viewed_page
            stats.most_viewed_page_views = most_viewed_count
            stats.desktop_views = device_breakdown.get('desktop', 0)
            stats.mobile_views = device_breakdown.get('mobile', 0)
            stats.tablet_views = device_breakdown.get('tablet', 0)
            stats.direct_traffic = direct_count
            stats.search_traffic = search_count
            stats.social_traffic = social_count
            stats.referral_traffic = referral_count
            stats.save()

        return stats


class UserActivity(models.Model):
    """Track user activity and engagement"""

    ACTIVITY_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('view_page', 'Page View'),
        ('comment', 'Comment Posted'),
        ('blog_post', 'Blog Post Created'),
        ('event_register', 'Event Registration'),
        ('prayer_request', 'Prayer Request'),
        ('ministry_join', 'Ministry Joined'),
        ('profile_update', 'Profile Updated'),
        ('download', 'File Downloaded'),
        ('search', 'Search Performed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.CharField(max_length=255)

    # Related object (optional)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional data
    metadata = models.JSONField(default=dict, blank=True)

    # Request information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class ConversionGoal(models.Model):
    """Define and track conversion goals"""

    GOAL_TYPE_CHOICES = [
        ('page_visit', 'Page Visit'),
        ('form_submission', 'Form Submission'),
        ('download', 'File Download'),
        ('registration', 'User Registration'),
        ('event_signup', 'Event Signup'),
        ('newsletter_signup', 'Newsletter Signup'),
        ('prayer_request', 'Prayer Request'),
        ('ministry_join', 'Ministry Join'),
        ('custom_event', 'Custom Event'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)

    # Goal definition
    target_url = models.CharField(max_length=500, blank=True, help_text="URL pattern for page visit goals")
    event_category = models.CharField(max_length=100, blank=True, help_text="Event category for custom goals")
    event_action = models.CharField(max_length=100, blank=True, help_text="Event action for custom goals")

    # Goal value (optional)
    value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Conversion Goal')
        verbose_name_plural = _('Conversion Goals')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_conversions(self, start_date=None, end_date=None):
        """Get conversion count for date range"""
        if self.goal_type == 'page_visit':
            queryset = PageView.objects.filter(path__icontains=self.target_url)
        else:
            # Handle other goal types as needed
            return 0

        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)

        return queryset.count()
