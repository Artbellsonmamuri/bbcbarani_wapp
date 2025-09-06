from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import json

User = get_user_model()


class ContentSection(models.Model):
    """Base model for all CMS content sections"""

    SECTION_TYPES = [
        ('welcome_screen', 'Welcome Screen'),
        ('schedule', 'Schedule of Services'),
        ('who_we_are', 'Who We Are'),
        ('articles_of_faith', 'Articles of Faith'),
        ('call_to_salvation', 'Call to Salvation'),
        ('contact', 'Contact Us'),
        ('blog_post', 'Blog Post'),
        ('page', 'Custom Page'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]

    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    body = RichTextUploadingField(blank=True)
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short description for previews")

    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO title (60-70 chars)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (150-160 chars)")
    meta_keywords = models.CharField(max_length=255, blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True)

    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    publish_date = models.DateTimeField(blank=True, null=True)

    # Multi-language support
    language = models.CharField(max_length=10, default='en')

    # Structured content (JSON for flexible layouts)
    structured_content = models.JSONField(default=dict, blank=True)

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sections')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_sections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Version control
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    # Display order
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']
        unique_together = [['section_type', 'language'], ['slug']]
        verbose_name = _('Content Section')
        verbose_name_plural = _('Content Sections')

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.title}"

    def get_absolute_url(self):
        if self.section_type == 'blog_post':
            return reverse('blog:detail', kwargs={'slug': self.slug})
        elif self.section_type == 'page':
            return reverse('cms:page', kwargs={'slug': self.slug})
        return reverse('cms:section', kwargs={'section_type': self.section_type})

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class WelcomeScreen(models.Model):
    """Specific model for welcome screen content"""
    content_section = models.OneToOneField(ContentSection, on_delete=models.CASCADE, primary_key=True)

    # Welcome message
    welcome_message = models.TextField(max_length=500)
    subtitle = models.CharField(max_length=255, blank=True)

    # Pastor information
    pastor_name = models.CharField(max_length=100)
    pastor_title = models.CharField(max_length=100, default="Senior Pastor")
    pastor_photo = models.ImageField(upload_to='pastor/', blank=True, null=True)
    pastor_bio = models.TextField(blank=True)

    # Church logo
    church_logo = models.ImageField(upload_to='logos/', blank=True, null=True)

    # Carousel images
    carousel_images = models.ManyToManyField('media_manager.Media', blank=True, related_name='welcome_carousels')

    # Call to action
    cta_text = models.CharField(max_length=100, blank=True, default="Join Us for Worship")
    cta_link = models.URLField(blank=True)

    class Meta:
        verbose_name = _('Welcome Screen')
        verbose_name_plural = _('Welcome Screens')

    def __str__(self):
        return f"Welcome Screen - {self.pastor_name}"


class ServiceSchedule(models.Model):
    """Service schedule management"""
    content_section = models.OneToOneField(ContentSection, on_delete=models.CASCADE, primary_key=True)

    # Service details
    service_name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=20, choices=[
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)

    # Location
    location_name = models.CharField(max_length=255)
    address = models.TextField()

    # Live streaming
    live_stream_enabled = models.BooleanField(default=False)
    live_stream_url = models.URLField(blank=True)
    live_stream_platform = models.CharField(max_length=50, blank=True, 
                                          choices=[('youtube', 'YouTube'), ('facebook', 'Facebook'), ('custom', 'Custom')])

    # Additional info
    description = models.TextField(blank=True)
    special_notes = models.TextField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'day_of_week', 'start_time']
        verbose_name = _('Service Schedule')
        verbose_name_plural = _('Service Schedules')

    def __str__(self):
        return f"{self.service_name} - {self.get_day_of_week_display()} {self.start_time}"


class HeaderFooter(models.Model):
    """Header and footer content management"""

    SECTION_CHOICES = [
        ('header', 'Header'),
        ('footer', 'Footer'),
    ]

    section = models.CharField(max_length=20, choices=SECTION_CHOICES)
    content = models.JSONField(default=dict, help_text="Store menu items, links, and other header/footer data")

    # Header specific fields
    show_language_switcher = models.BooleanField(default=True)
    show_search = models.BooleanField(default=True)

    # Footer specific fields  
    copyright_text = models.CharField(max_length=255, blank=True)
    footer_message = models.TextField(blank=True)

    # Social media links
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    # Contact info in footer
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Header/Footer')
        verbose_name_plural = _('Headers & Footers')
        unique_together = ['section']

    def __str__(self):
        return f"{self.get_section_display()} Configuration"


class SEOSettings(models.Model):
    """Global SEO settings and site-wide configuration"""

    site_name = models.CharField(max_length=100, default="Bible Baptist Church Barani")
    site_tagline = models.CharField(max_length=255, blank=True)
    site_description = models.TextField(max_length=500)

    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    google_tag_manager_id = models.CharField(max_length=50, blank=True)

    # Verification codes
    google_site_verification = models.CharField(max_length=100, blank=True)
    bing_site_verification = models.CharField(max_length=100, blank=True)

    # Social media defaults
    default_og_image = models.ImageField(upload_to='seo/', blank=True, null=True)
    facebook_app_id = models.CharField(max_length=50, blank=True)

    # Miscellaneous
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('SEO Settings')
        verbose_name_plural = _('SEO Settings')

    def __str__(self):
        return f"SEO Settings - {self.site_name}"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SEOSettings.objects.exists():
            raise ValueError('Only one SEO Settings instance is allowed')
        super().save(*args, **kwargs)


class ContentRevision(models.Model):
    """Version control for content sections"""

    content_section = models.ForeignKey(ContentSection, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.PositiveIntegerField()

    # Snapshot of content at this revision
    title = models.CharField(max_length=255)
    body = models.TextField()
    structured_content = models.JSONField(default=dict)

    # Revision metadata
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    change_summary = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-revision_number']
        unique_together = ['content_section', 'revision_number']
        verbose_name = _('Content Revision')
        verbose_name_plural = _('Content Revisions')

    def __str__(self):
        return f"{self.content_section.title} - Rev {self.revision_number}"
