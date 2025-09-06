from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from apps.media_manager.models import Media

User = get_user_model()


class EventCategory(models.Model):
    """Categories for organizing events"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff")
    icon = models.CharField(max_length=50, default="fas fa-calendar")

    # Settings
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Event Category')
        verbose_name_plural = _('Event Categories')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Event(models.Model):
    """Church events with RSVP and attendee tracking"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Basic information
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = RichTextUploadingField()
    short_description = models.CharField(max_length=255, help_text="Brief description for previews")

    # Scheduling
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')

    # Location
    location_name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True, help_text="Zoom/Teams/etc link for virtual events")

    # Organization
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    co_organizers = models.ManyToManyField(User, blank=True, related_name='co_organized_events')

    # Registration/RSVP
    requires_rsvp = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(blank=True, null=True)
    registration_deadline = models.DateTimeField(blank=True, null=True)
    allow_guest_registration = models.BooleanField(default=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Media
    featured_image = models.ForeignKey(Media, on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='featured_events',
                                     limit_choices_to={'media_type': 'image'})
    gallery_images = models.ManyToManyField(Media, blank=True, 
                                          related_name='event_galleries',
                                          limit_choices_to={'media_type': 'image'})

    # Additional information
    contact_person = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='contact_for_events')
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # Settings
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(default=dict, blank=True)

    # Notifications
    send_reminders = models.BooleanField(default=True)
    reminder_schedule = models.JSONField(default=dict, blank=True, 
                                       help_text="Schedule for sending reminders (days before event)")

    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%m/%d/%Y')}"

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        return self.start_datetime > timezone.now()

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime

    @property
    def is_past(self):
        return self.end_datetime < timezone.now()

    @property
    def registration_count(self):
        return self.registrations.filter(status='confirmed').count()

    @property
    def spots_available(self):
        if self.max_attendees:
            return max(0, self.max_attendees - self.registration_count)
        return None

    @property
    def is_registration_open(self):
        if not self.requires_rsvp:
            return False

        now = timezone.now()

        # Check if registration deadline has passed
        if self.registration_deadline and now > self.registration_deadline:
            return False

        # Check if event has started
        if now >= self.start_datetime:
            return False

        # Check if spots are available
        if self.max_attendees and self.registration_count >= self.max_attendees:
            return False

        return True


class EventRegistration(models.Model):
    """RSVP and registration tracking for events"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlist', 'Waitlist'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')

    # Registrant information
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    guest_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)

    # Registration details
    number_of_attendees = models.PositiveIntegerField(default=1)
    attendee_names = models.TextField(blank=True, help_text="Names of additional attendees")
    dietary_restrictions = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)

    # Status and payment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
        ('refunded', 'Refunded'),
    ], default='pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Check-in
    checked_in_at = models.DateTimeField(blank=True, null=True)
    checked_in_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='checked_in_registrations')

    # Notes
    registration_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['event', 'user', 'guest_email']
        ordering = ['registered_at']
        verbose_name = _('Event Registration')
        verbose_name_plural = _('Event Registrations')

    def __str__(self):
        return f"{self.get_registrant_name()} - {self.event.title}"

    def get_registrant_name(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.guest_name or "Anonymous"

    def get_registrant_email(self):
        if self.user:
            return self.user.email
        return self.guest_email

    @property
    def is_guest_registration(self):
        return self.user is None

    @property
    def total_cost(self):
        return self.payment_amount * self.number_of_attendees


class EventAttendance(models.Model):
    """Track actual attendance for events"""

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_records')
    registration = models.OneToOneField(EventRegistration, on_delete=models.CASCADE, blank=True, null=True)

    # Walk-in attendee (no registration)
    walk_in_name = models.CharField(max_length=100, blank=True)
    walk_in_email = models.EmailField(blank=True)

    # Attendance details
    checked_in_at = models.DateTimeField(auto_now_add=True)
    checked_in_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checked_in_attendees')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _('Event Attendance')
        verbose_name_plural = _('Event Attendance Records')

    def __str__(self):
        if self.registration:
            return f"{self.registration.get_registrant_name()} attended {self.event.title}"
        return f"{self.walk_in_name} attended {self.event.title}"
