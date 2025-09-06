from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.utils import timezone
from .models import (
    PageView, SiteStatistics, UserActivity, ConversionGoal
)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'user', 'device_type', 'country', 'timestamp')
    list_filter = ('device_type', 'browser', 'os', 'country', 'timestamp')
    search_fields = ('path', 'title', 'user__username', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Page Information', {
            'fields': ('url', 'path', 'title')
        }),
        ('Visitor Information', {
            'fields': ('user', 'session_key', 'ip_address')
        }),
        ('Device & Browser', {
            'fields': ('device_type', 'browser', 'os', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Location', {
            'fields': ('country', 'city'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('referer', 'duration', 'timestamp')
        }),
    )

    actions = ['generate_daily_stats']

    def generate_daily_stats(self, request, queryset):
        """Generate daily statistics for selected dates"""
        dates = queryset.values_list('timestamp__date', flat=True).distinct()
        generated = 0

        for date in dates:
            SiteStatistics.generate_for_date(date)
            generated += 1

        self.message_user(request, f'Generated statistics for {generated} days.')
    generate_daily_stats.short_description = 'Generate daily statistics'


@admin.register(SiteStatistics)
class SiteStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_page_views', 'unique_visitors', 'mobile_percentage', 'bounce_rate')
    list_filter = ('date',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'

    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Traffic Overview', {
            'fields': ('total_page_views', 'unique_visitors', 'registered_user_views')
        }),
        ('Popular Content', {
            'fields': ('most_viewed_page', 'most_viewed_page_views')
        }),
        ('Device Breakdown', {
            'fields': ('desktop_views', 'mobile_views', 'tablet_views'),
            'classes': ('collapse',)
        }),
        ('Traffic Sources', {
            'fields': ('direct_traffic', 'search_traffic', 'social_traffic', 'referral_traffic'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('avg_session_duration', 'bounce_rate'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def mobile_percentage(self, obj):
        total = obj.total_page_views
        if total > 0:
            mobile_pct = (obj.mobile_views / total) * 100
            return f"{mobile_pct:.1f}%"
        return "0%"
    mobile_percentage.short_description = 'Mobile %'

    actions = ['regenerate_statistics']

    def regenerate_statistics(self, request, queryset):
        """Regenerate statistics for selected dates"""
        regenerated = 0
        for stat in queryset:
            SiteStatistics.generate_for_date(stat.date)
            regenerated += 1

        self.message_user(request, f'Regenerated {regenerated} statistics records.')
    regenerate_statistics.short_description = 'Regenerate statistics'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'description')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(ConversionGoal)
class ConversionGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal_type', 'is_active', 'conversion_count', 'created_by')
    list_filter = ('goal_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Goal Information', {
            'fields': ('name', 'description', 'goal_type', 'is_active')
        }),
        ('Goal Definition', {
            'fields': ('target_url', 'event_category', 'event_action', 'value')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def conversion_count(self, obj):
        return obj.get_conversions()
    conversion_count.short_description = 'Conversions'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
