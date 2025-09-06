from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
from .models import (
    PageView, SiteStatistics, UserActivity, ConversionGoal
)
from .services import AnalyticsService


class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Main analytics dashboard"""
    template_name = 'analytics/dashboard.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date range from query params
        date_range = self.request.GET.get('range', '7')  # Default 7 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(date_range))

        # Get analytics service
        service = AnalyticsService()

        # Overview metrics
        overview = service.get_overview_metrics(start_date, end_date)

        # Popular content
        popular_pages = service.get_popular_pages(start_date, end_date, limit=10)

        # Device and browser stats
        device_stats = service.get_device_breakdown(start_date, end_date)

        # Traffic sources
        traffic_sources = service.get_traffic_sources(start_date, end_date)

        # Daily trends
        daily_trends = service.get_daily_trends(start_date, end_date)

        # Recent activity
        recent_activity = UserActivity.objects.order_by('-timestamp')[:20]

        context.update({
            'date_range': date_range,
            'start_date': start_date,
            'end_date': end_date,
            'overview': overview,
            'popular_pages': popular_pages,
            'device_stats': device_stats,
            'traffic_sources': traffic_sources,
            'daily_trends': daily_trends,
            'recent_activity': recent_activity,
        })

        return context


@staff_member_required
def analytics_api_overview(request):
    """API endpoint for overview metrics"""

    # Date range
    days = int(request.GET.get('days', 7))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    service = AnalyticsService()
    metrics = service.get_overview_metrics(start_date, end_date)

    # Previous period comparison
    prev_start = start_date - timedelta(days=days)
    prev_end = start_date
    prev_metrics = service.get_overview_metrics(prev_start, prev_end)

    # Calculate changes
    changes = {}
    for key in ['total_views', 'unique_visitors', 'avg_session_duration', 'bounce_rate']:
        current = metrics.get(key, 0)
        previous = prev_metrics.get(key, 0)
        if previous > 0:
            change = ((current - previous) / previous) * 100
            changes[key] = round(change, 1)
        else:
            changes[key] = 0 if current == 0 else 100

    return JsonResponse({
        'current': metrics,
        'previous': prev_metrics,
        'changes': changes,
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'days': days
        }
    })


@staff_member_required
def track_page_view(request):
    """Track a page view (usually called via AJAX)"""

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)

        # Create page view record
        page_view = PageView.objects.create(
            url=data.get('url', ''),
            path=data.get('path', ''),
            title=data.get('title', ''),
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referer=request.META.get('HTTP_REFERER', ''),
        )

        return JsonResponse({'success': True, 'id': page_view.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def user_analytics_summary(request):
    """Get analytics summary for current user"""

    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Quick metrics for header/widget display
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    today_views = PageView.objects.filter(timestamp__date=today).count()
    yesterday_views = PageView.objects.filter(timestamp__date=yesterday).count()

    # Recent activity count
    recent_activity = UserActivity.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).count()

    return JsonResponse({
        'today_views': today_views,
        'yesterday_views': yesterday_views,
        'view_change': today_views - yesterday_views,
        'recent_activity': recent_activity,
    })
