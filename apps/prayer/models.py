from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class PrayerCategory(models.Model):
    """Categories for organizing prayer requests"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="fas fa-praying-hands")
    color = models.CharField(max_length=7, default="#007bff")
    is_public = models.BooleanField(default=True, help_text="Show in public prayer request form")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Prayer Category')
        verbose_name_plural = _('Prayer Categories')

    def __str__(self):
        return self.name


class PrayerRequest(models.Model):
    """Model for storing prayer requests from the public and members"""

    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewing', 'Under Review'),
        ('approved', 'Approved'),
        ('praying', 'Being Prayed For'),
        ('answered', 'Answered'),
        ('archived', 'Archived'),
    ]

    PRIVACY_CHOICES = [
        ('public', 'Public - Can be shared with prayer team'),
        ('private', 'Private - Keep confidential'),
        ('anonymous', 'Anonymous - Share without name'),
    ]

    # Requester information
    requester_name = models.CharField(max_length=100, blank=True, help_text="Optional")
    email = models.EmailField(blank=True, help_text="Optional - for updates")
    phone = models.CharField(max_length=20, blank=True)

    # If submitted by registered user
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='prayer_requests')

    # Request details
    category = models.ForeignKey(PrayerCategory, on_delete=models.SET_NULL, blank=True, null=True)
    subject = models.CharField(max_length=255, help_text="Brief description of prayer request")
    message = models.TextField(max_length=2000, help_text="Detailed prayer request")

    # Privacy and sharing
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='private')
    share_with_prayer_team = models.BooleanField(default=False)
    share_updates_via_email = models.BooleanField(default=False)

    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    urgent = models.BooleanField(default=False)

    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='assigned_prayers',
                                   limit_choices_to={'role__in': ['super_admin', 'admin', 'ministry_lead']})

    # Follow-up
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_notes = models.TextField(blank=True)

    # Admin notes (not visible to requester)
    admin_notes = models.TextField(blank=True, help_text="Internal notes for staff only")

    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    answered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = _('Prayer Request')
        verbose_name_plural = _('Prayer Requests')

    def __str__(self):
        return f"{self.subject} - {self.get_requester_name()}"

    def get_requester_name(self):
        """Get the name of the person who submitted the request"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        elif self.requester_name:
            return self.requester_name
        else:
            return "Anonymous"

    def get_contact_email(self):
        """Get contact email for the requester"""
        if self.user and self.user.email:
            return self.user.email
        return self.email

    def can_be_shared_publicly(self):
        """Check if prayer request can be shared publicly"""
        return self.privacy_level in ['public', 'anonymous'] and self.status == 'approved'

    def get_public_display_name(self):
        """Get name for public display based on privacy settings"""
        if self.privacy_level == 'anonymous':
            return "Anonymous"
        return self.get_requester_name()

    def notify_staff(self):
        """Send notification to staff about new prayer request"""
        if self.urgent:
            # Send urgent notification
            pass
        # TODO: Implement notification system


class PrayerResponse(models.Model):
    """Staff responses and updates to prayer requests"""

    prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField(help_text="Response or update message")
    is_public = models.BooleanField(default=False, help_text="Share with requester")
    is_internal = models.BooleanField(default=True, help_text="Internal staff note")

    # Prayer team sharing
    shared_with_prayer_team = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Prayer Response')
        verbose_name_plural = _('Prayer Responses')

    def __str__(self):
        return f"Response to: {self.prayer_request.subject}"


class PrayerTeam(models.Model):
    """Prayer team members who can access prayer requests"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='prayer_team_profile')

    # Team information
    team_role = models.CharField(max_length=100, default="Prayer Team Member")
    specializations = models.CharField(max_length=255, blank=True, 
                                     help_text="Areas of prayer focus (e.g., healing, missions)")

    # Contact preferences
    email_notifications = models.BooleanField(default=True)
    urgent_notifications = models.BooleanField(default=True)
    daily_digest = models.BooleanField(default=False)

    # Settings
    is_active = models.BooleanField(default=True)
    can_respond_to_requests = models.BooleanField(default=True)

    joined_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _('Prayer Team Member')
        verbose_name_plural = _('Prayer Team Members')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team_role}"


class PrayerWall(models.Model):
    """Public prayer wall for sharing answered prayers and testimonies"""

    title = models.CharField(max_length=255)
    content = models.TextField()

    # Attribution
    author_name = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    # Related prayer request (if applicable)
    related_prayer_request = models.ForeignKey(PrayerRequest, on_delete=models.SET_NULL, blank=True, null=True)

    # Moderation
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='approved_prayer_wall_posts')

    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = _('Prayer Wall Post')
        verbose_name_plural = _('Prayer Wall Posts')

    def __str__(self):
        return self.title

    def get_author_name(self):
        if self.author:
            return self.author.get_full_name()
        return self.author_name or "Anonymous"
