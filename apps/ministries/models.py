from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from apps.media_manager.models import Media

User = get_user_model()


class MinistryCategory(models.Model):
    """Categories for organizing ministries"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class (e.g., fas fa-heart)")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Ministry Category')
        verbose_name_plural = _('Ministry Categories')

    def __str__(self):
        return self.name


class Ministry(models.Model):
    """Church ministries with carousel images, descriptions, and leadership"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    short_description = models.CharField(max_length=255, help_text="Brief description for cards/previews")
    full_description = RichTextUploadingField()

    # Visual elements
    icon_type = models.CharField(max_length=20, choices=[
        ('font', 'Font Icon'),
        ('image', 'Custom Image'),
    ], default='font')
    font_icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome class (e.g., fas fa-cross)")
    custom_icon = models.ForeignKey(Media, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='ministry_icons', 
                                   limit_choices_to={'media_type': 'image'})

    # Carousel images for ministry detail page
    carousel_images = models.ManyToManyField(Media, blank=True, 
                                           related_name='ministry_carousels',
                                           limit_choices_to={'media_type': 'image'})

    # Organization
    category = models.ForeignKey(MinistryCategory, on_delete=models.SET_NULL, blank=True, null=True)

    # Leadership
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                              related_name='led_ministries',
                              limit_choices_to={'role__in': ['admin', 'ministry_lead']})
    co_leaders = models.ManyToManyField(User, blank=True, 
                                       related_name='co_led_ministries',
                                       limit_choices_to={'role__in': ['admin', 'ministry_lead', 'member']})

    # Contact information
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    meeting_location = models.CharField(max_length=255, blank=True)
    meeting_schedule = models.TextField(blank=True, help_text="When does this ministry meet?")

    # Settings
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    allow_public_contact = models.BooleanField(default=True)
    requires_membership = models.BooleanField(default=False)

    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # Display order
    order = models.PositiveIntegerField(default=0)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_ministries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = _('Ministry')
        verbose_name_plural = _('Ministries')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ministries:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def display_icon(self):
        """Get the icon to display (font or custom image)"""
        if self.icon_type == 'image' and self.custom_icon:
            return {'type': 'image', 'url': self.custom_icon.file.url, 'alt': self.custom_icon.alt_text}
        elif self.icon_type == 'font' and self.font_icon:
            return {'type': 'font', 'class': self.font_icon}
        else:
            return {'type': 'font', 'class': 'fas fa-church'}  # Default icon

    def get_member_count(self):
        """Get number of members in this ministry"""
        return self.members.filter(ministry_affiliations=self).count()


class MinistryMember(models.Model):
    """Track ministry membership and roles"""

    ROLE_CHOICES = [
        ('member', 'Member'),
        ('volunteer', 'Volunteer'),
        ('coordinator', 'Coordinator'),
        ('assistant_leader', 'Assistant Leader'),
    ]

    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name='ministry_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ministry_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    # Additional details
    skills = models.CharField(max_length=255, blank=True, help_text="Skills this person brings to the ministry")
    availability = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ['ministry', 'user']
        verbose_name = _('Ministry Member')
        verbose_name_plural = _('Ministry Members')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.ministry.title} ({self.get_role_display()})"


class MinistryEvent(models.Model):
    """Events specific to ministries"""
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name='ministry_events')
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Schedule
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)

    # Registration
    requires_registration = models.BooleanField(default=False)
    max_attendees = models.PositiveIntegerField(blank=True, null=True)
    registration_deadline = models.DateTimeField(blank=True, null=True)

    # Contact
    contact_person = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # Media
    featured_image = models.ForeignKey(Media, on_delete=models.SET_NULL, blank=True, null=True,
                                     limit_choices_to={'media_type': 'image'})

    # Settings
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        verbose_name = _('Ministry Event')
        verbose_name_plural = _('Ministry Events')

    def __str__(self):
        return f"{self.ministry.title} - {self.title}"

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.start_datetime > timezone.now()

    @property
    def registration_count(self):
        return self.registrations.filter(status='confirmed').count()

    @property
    def spots_available(self):
        if self.max_attendees:
            return max(0, self.max_attendees - self.registration_count)
        return None


# Import RichTextUploadingField after Media model is defined
from ckeditor_uploader.fields import RichTextUploadingField
# Update Ministry model to use RichTextUploadingField
Ministry._meta.get_field('full_description').__class__ = RichTextUploadingField
