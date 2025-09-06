from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count
from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    AnnouncementBanner, NotificationQueue
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_type', 'delivery_methods', 'is_active', 'recipient_count')
    list_filter = ('trigger_type', 'is_active', 'send_email', 'send_in_app', 'send_sms')
    search_fields = ('name', 'email_subject', 'in_app_title')
    filter_horizontal = ('send_to_specific_users',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'trigger_type', 'is_active', 'delay_minutes')
        }),
        ('Email Template', {
            'fields': ('send_email', 'email_subject', 'email_body'),
            'classes': ('collapse',)
        }),
        ('In-App Template', {
            'fields': ('send_in_app', 'in_app_title', 'in_app_message'),
            'classes': ('collapse',)
        }),
        ('SMS Template', {
            'fields': ('send_sms', 'sms_message'),
            'classes': ('collapse',)
        }),
        ('Recipients', {
            'fields': (
                'send_to_admins', 'send_to_ministry_leads', 'send_to_members',
                'send_to_subscribers', 'send_to_specific_users'
            ),
            'classes': ('collapse',)
        }),
    )

    def delivery_methods(self, obj):
        methods = []
        if obj.send_email:
            methods.append('<span class="badge bg-primary">Email</span>')
        if obj.send_in_app:
            methods.append('<span class="badge bg-success">In-App</span>')
        if obj.send_sms:
            methods.append('<span class="badge bg-info">SMS</span>')
        return format_html(' '.join(methods)) if methods else '-'
    delivery_methods.short_description = 'Delivery Methods'

    def recipient_count(self, obj):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        count = 0
        if obj.send_to_admins:
            count += User.objects.filter(is_staff=True).count()
        if obj.send_to_ministry_leads:
            count += User.objects.filter(role='ministry_lead').count()
        if obj.send_to_members:
            count += User.objects.filter(is_active=True).count()
        count += obj.send_to_specific_users.count()
        return count
    recipient_count.short_description = 'Recipients'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'email_sent', 'created_at')
    search_fields = ('title', 'message', 'recipient__username', 'recipient__email')
    readonly_fields = ('read_at', 'email_sent_at', 'sms_sent_at', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Notification Details', {
            'fields': ('title', 'message', 'notification_type', 'priority', 'recipient', 'sender')
        }),
        ('Content Reference', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'expires_at')
        }),
        ('Delivery Status', {
            'fields': ('email_sent', 'email_sent_at', 'sms_sent', 'sms_sent_at'),
            'classes': ('collapse',)
        }),
        ('Action', {
            'fields': ('action_url', 'action_text')
        }),
        ('Metadata', {
            'fields': ('extra_data', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread', 'delete_old_notifications']

    def mark_as_read(self, request, queryset):
        updated = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        messages.success(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark as read'

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        messages.success(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'

    def delete_old_notifications(self, request, queryset):
        # Delete notifications older than 30 days and already read
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = queryset.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()[0]
        messages.success(request, f'{deleted_count} old notifications deleted.')
    delete_old_notifications.short_description = 'Delete old read notifications'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_enabled', 'email_frequency', 'in_app_enabled', 'notification_summary')
    list_filter = ('email_enabled', 'email_frequency', 'in_app_enabled', 'sms_enabled')
    search_fields = ('user__username', 'user__email')

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Settings', {
            'fields': ('email_enabled', 'email_frequency')
        }),
        ('In-App Settings', {
            'fields': ('in_app_enabled', 'show_desktop_notifications')
        }),
        ('SMS Settings', {
            'fields': ('sms_enabled', 'phone_number'),
            'classes': ('collapse',)
        }),
        ('Notification Types', {
            'fields': (
                'blog_notifications', 'event_notifications', 'comment_notifications',
                'prayer_notifications', 'system_notifications', 'marketing_notifications'
            )
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_enabled', 'quiet_start_time', 'quiet_end_time'),
            'classes': ('collapse',)
        }),
    )

    def notification_summary(self, obj):
        enabled = []
        if obj.blog_notifications:
            enabled.append('Blog')
        if obj.event_notifications:
            enabled.append('Events')
        if obj.comment_notifications:
            enabled.append('Comments')
        if obj.system_notifications:
            enabled.append('System')
        return ', '.join(enabled) if enabled else 'None'
    notification_summary.short_description = 'Enabled Types'


@admin.register(AnnouncementBanner)
class AnnouncementBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'position', 'is_active', 'is_currently_active', 'created_at')
    list_filter = ('banner_type', 'position', 'is_active', 'show_to_members_only', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Content', {
            'fields': ('title', 'message', 'banner_type')
        }),
        ('Display Settings', {
            'fields': (
                'is_active', 'position', 'is_dismissible',
                'show_on_all_pages', 'specific_pages'
            )
        }),
        ('Scheduling', {
            'fields': ('start_datetime', 'end_datetime'),
            'classes': ('collapse',)
        }),
        ('Targeting', {
            'fields': (
                'show_to_all_users', 'show_to_members_only', 'show_to_guests_only'
            ),
            'classes': ('collapse',)
        }),
        ('Action Button', {
            'fields': ('action_text', 'action_url', 'action_opens_new_tab'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_currently_active(self, obj):
        return obj.is_currently_active
    is_currently_active.boolean = True
    is_currently_active.short_description = 'Active Now'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(NotificationQueue)
class NotificationQueueAdmin(admin.ModelAdmin):
    list_display = ('notification_template', 'status', 'recipient_count', 'scheduled_for', 'attempts')
    list_filter = ('status', 'notification_template', 'scheduled_for')
    readonly_fields = ('attempts', 'last_attempt_at', 'created_at', 'updated_at')
    filter_horizontal = ('recipients',)

    fieldsets = (
        ('Queue Details', {
            'fields': ('notification_template', 'recipients', 'scheduled_for', 'status')
        }),
        ('Content Reference', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Template Data', {
            'fields': ('context_data',),
            'classes': ('collapse',)
        }),
        ('Processing Status', {
            'fields': ('attempts', 'last_attempt_at', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def recipient_count(self, obj):
        return obj.recipients.count()
    recipient_count.short_description = 'Recipients'

    actions = ['retry_failed_notifications']

    def retry_failed_notifications(self, request, queryset):
        updated = queryset.filter(status='failed').update(
            status='pending',
            error_message='',
            scheduled_for=timezone.now()
        )
        messages.success(request, f'{updated} notifications queued for retry.')
    retry_failed_notifications.short_description = 'Retry failed notifications'
