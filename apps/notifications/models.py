from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json

User = get_user_model()


class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""

    TRIGGER_CHOICES = [
        ('blog_post_published', 'Blog Post Published'),
        ('comment_submitted', 'Comment Submitted'),
        ('comment_approved', 'Comment Approved'),
        ('event_created', 'Event Created'),
        ('event_registration', 'Event Registration'),
        ('prayer_request', 'Prayer Request Submitted'),
        ('user_registered', 'User Registered'),
        ('ministry_joined', 'Ministry Joined'),
        ('content_updated', 'Content Updated'),
        ('system_maintenance', 'System Maintenance'),
        ('custom', 'Custom Notification'),
    ]

    name = models.CharField(max_length=100)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES)

    # Email template
    email_subject = models.CharField(max_length=255, blank=True)
    email_body = models.TextField(blank=True, help_text="HTML email template with variables")
    send_email = models.BooleanField(default=True)

    # In-app notification template
    in_app_title = models.CharField(max_length=255, blank=True)
    in_app_message = models.TextField(blank=True)
    send_in_app = models.BooleanField(default=True)

    # SMS template (for future use)
    sms_message = models.CharField(max_length=160, blank=True)
    send_sms = models.BooleanField(default=False)

    # Settings
    is_active = models.BooleanField(default=True)
    delay_minutes = models.PositiveIntegerField(default=0, help_text="Delay sending by X minutes")

    # Recipients
    send_to_admins = models.BooleanField(default=False)
    send_to_ministry_leads = models.BooleanField(default=False)
    send_to_members = models.BooleanField(default=False)
    send_to_subscribers = models.BooleanField(default=False)
    send_to_specific_users = models.ManyToManyField(User, blank=True, related_name='notification_recipients')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"


class Notification(models.Model):
    """Individual notifications sent to users"""

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('announcement', 'Announcement'),
    ]

    # Basic information
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')

    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='sent_notifications')

    # Content reference (generic foreign key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    # Delivery tracking
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    sms_sent = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(blank=True, null=True)

    # Action link
    action_url = models.URLField(blank=True, help_text="Link to relevant content")
    action_text = models.CharField(max_length=100, blank=True, help_text="Text for action button")

    # Metadata
    extra_data = models.JSONField(default=dict, blank=True, help_text="Additional data for the notification")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When notification expires")

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} -> {self.recipient.username}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def get_icon(self):
        """Get icon for notification type"""
        icons = {
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle', 
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-times-circle',
            'announcement': 'fas fa-bullhorn',
        }
        return icons.get(self.notification_type, 'fas fa-bell')

    def get_color_class(self):
        """Get CSS class for notification type"""
        colors = {
            'info': 'text-info',
            'success': 'text-success',
            'warning': 'text-warning', 
            'error': 'text-danger',
            'announcement': 'text-primary',
        }
        return colors.get(self.notification_type, 'text-info')


class NotificationPreference(models.Model):
    """User preferences for receiving notifications"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')

    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Summary'),
        ('never', 'Never'),
    ], default='immediate')

    # In-app preferences
    in_app_enabled = models.BooleanField(default=True)
    show_desktop_notifications = models.BooleanField(default=False)

    # SMS preferences
    sms_enabled = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)

    # Notification types
    blog_notifications = models.BooleanField(default=True)
    event_notifications = models.BooleanField(default=True)
    comment_notifications = models.BooleanField(default=True)
    prayer_notifications = models.BooleanField(default=False, help_text="For ministry leads only")
    system_notifications = models.BooleanField(default=True)
    marketing_notifications = models.BooleanField(default=False)

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_start_time = models.TimeField(blank=True, null=True, help_text="Start of quiet hours")
    quiet_end_time = models.TimeField(blank=True, null=True, help_text="End of quiet hours")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')

    def __str__(self):
        return f"{self.user.username} - Notifications"

    def should_send_email(self):
        """Check if email notifications should be sent"""
        return self.email_enabled and self.email_frequency != 'never'

    def should_send_in_app(self):
        """Check if in-app notifications should be sent"""
        return self.in_app_enabled

    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_enabled or not self.quiet_start_time or not self.quiet_end_time:
            return False

        current_time = timezone.now().time()
        return self.quiet_start_time <= current_time <= self.quiet_end_time


class AnnouncementBanner(models.Model):
    """Site-wide announcement banners"""

    BANNER_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Alert/Danger'),
        ('primary', 'Primary'),
    ]

    POSITION_CHOICES = [
        ('top', 'Top of Page'),
        ('bottom', 'Bottom of Page'),
        ('modal', 'Modal Popup'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='info')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='top')

    # Display settings
    is_active = models.BooleanField(default=True)
    is_dismissible = models.BooleanField(default=True)
    show_on_all_pages = models.BooleanField(default=True)
    specific_pages = models.TextField(blank=True, help_text="Comma-separated list of page URLs")

    # Scheduling
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)

    # Targeting
    show_to_all_users = models.BooleanField(default=True)
    show_to_members_only = models.BooleanField(default=False)
    show_to_guests_only = models.BooleanField(default=False)

    # Action button
    action_text = models.CharField(max_length=100, blank=True)
    action_url = models.URLField(blank=True)
    action_opens_new_tab = models.BooleanField(default=False)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Announcement Banner')
        verbose_name_plural = _('Announcement Banners')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_currently_active(self):
        """Check if banner should be displayed now"""
        if not self.is_active:
            return False

        now = timezone.now()

        if self.start_datetime and now < self.start_datetime:
            return False

        if self.end_datetime and now > self.end_datetime:
            return False

        return True

    def should_show_to_user(self, user):
        """Check if banner should be shown to specific user"""
        if not self.is_currently_active:
            return False

        if self.show_to_all_users:
            return True

        if self.show_to_members_only and user.is_authenticated:
            return True

        if self.show_to_guests_only and not user.is_authenticated:
            return True

        return False


class NotificationQueue(models.Model):
    """Queue for delayed and batch notifications"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    notification_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(User, related_name='queued_notifications')

    # Content reference
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Template context data
    context_data = models.JSONField(default=dict, help_text="Data to populate template variables")

    # Scheduling
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Tracking
    attempts = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification Queue')
        verbose_name_plural = _('Notification Queue')
        ordering = ['scheduled_for']

    def __str__(self):
        return f"{self.notification_template.name} - {self.status}"
