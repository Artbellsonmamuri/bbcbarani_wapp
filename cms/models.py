"""
Bible Baptist Church CMS - Content Models
Complete model-driven CMS for church website
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

class BaseContentModel(models.Model):
    """Base model with common fields for all content"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    published = models.BooleanField(default=False, help_text="Check to make this content visible on the website")
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title

class Homepage(BaseContentModel):
    """Main homepage content - only one should be published at a time"""
    hero_title = models.CharField(max_length=200, help_text="Large hero title")
    hero_subtitle = models.CharField(max_length=300, blank=True, help_text="Subtitle under hero")
    hero_image = models.ImageField(upload_to='homepage/', blank=True, null=True)
    welcome_text = models.TextField(help_text="Main welcome message (supports HTML)")
    service_times = models.TextField(blank=True, help_text="Service times and info")
    featured_verse = models.TextField(blank=True, help_text="Bible verse for homepage")
    featured_verse_reference = models.CharField(max_length=100, blank=True)
    call_to_action_text = models.CharField(max_length=200, blank=True)
    call_to_action_url = models.CharField(max_length=200, blank=True)
    church_logo = models.ImageField(upload_to='homepage/', blank=True, null=True, help_text="Church logo (recommended: square format, 400x400px)")

    class Meta:
        verbose_name = "Homepage Content"
        verbose_name_plural = "Homepage Content"
        ordering = ['-updated_at']

class Page(BaseContentModel):
    """Static pages like About, Beliefs, Contact, etc."""
    content = models.TextField(help_text="Page content (supports HTML)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description")
    show_in_navigation = models.BooleanField(default=True, help_text="Show in main navigation menu")
    navigation_order = models.PositiveIntegerField(default=100, help_text="Order in navigation (lower = first)")
    featured_image = models.ImageField(upload_to='pages/', blank=True, null=True)
    
    class Meta:
        ordering = ['navigation_order', 'title']
        
    def get_absolute_url(self):
        return reverse('cms:page_detail', kwargs={'slug': self.slug})

class Post(BaseContentModel):
    """Blog posts and news items"""
    excerpt = models.TextField(blank=True, help_text="Short summary for listings")
    content = models.TextField(help_text="Full post content (supports HTML)")
    featured_image = models.ImageField(upload_to='posts/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    is_featured = models.BooleanField(default=False, help_text="Feature on homepage")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    class Meta:
        ordering = ['-created_at']
        
    def get_absolute_url(self):
        return reverse('cms:post_detail', kwargs={'slug': self.slug})

class Event(BaseContentModel):
    """Church events and activities"""
    description = models.TextField(help_text="Event description (supports HTML)")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    featured_image = models.ImageField(upload_to='events/', blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    registration_url = models.URLField(blank=True)
    max_attendees = models.PositiveIntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['start_date']
        
    def get_absolute_url(self):
        return reverse('cms:event_detail', kwargs={'slug': self.slug})
        
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()
        
    @property
    def is_past(self):
        return self.end_date and self.end_date < timezone.now()

class Ministry(BaseContentModel):
    """Church ministries and departments"""
    description = models.TextField(help_text="Ministry description (supports HTML)")
    leader_name = models.CharField(max_length=100, blank=True)
    leader_title = models.CharField(max_length=100, blank=True, help_text="e.g., Pastor, Director")
    leader_email = models.EmailField(blank=True)
    leader_phone = models.CharField(max_length=20, blank=True)
    meeting_time = models.CharField(max_length=200, blank=True, help_text="When does this ministry meet?")
    meeting_location = models.CharField(max_length=200, blank=True)
    featured_image = models.ImageField(upload_to='ministries/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    target_audience = models.CharField(max_length=100, blank=True, help_text="e.g., Adults, Youth, Children")
    
    class Meta:
        verbose_name_plural = "Ministries"
        ordering = ['title']
        
    def get_absolute_url(self):
        return reverse('cms:ministry_detail', kwargs={'slug': self.slug})

class MediaAsset(models.Model):
    """Reusable media files for the site"""
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='media_assets/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'mp3', 'mp4', 'mov'])]
    )
    file_type = models.CharField(max_length=20, choices=[
        ('image', 'Image'),
        ('document', 'Document'), 
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('other', 'Other')
    ], default='other')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return self.title
        
    @property
    def file_size_mb(self):
        try:
            return round(self.file.size / (1024 * 1024), 2)
        except:
            return 0

class HeroSlide(models.Model):
    """Hero carousel slides manageable through admin"""
    title = models.CharField(max_length=200, help_text="Main headline for this slide")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Optional subtitle/description")
    background_image = models.ImageField(upload_to='hero_slides/', help_text="Full-width background image (recommended: 1920x900px)")
    call_to_action_text = models.CharField(max_length=100, blank=True, help_text="Button text (e.g., 'Learn More')")
    call_to_action_url = models.CharField(max_length=200, blank=True, help_text="Button link URL")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    published = models.BooleanField(default=True, help_text="Show this slide on the website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Hero Carousel Slide"
        verbose_name_plural = "Hero Carousel Slides"
    
    def __str__(self):
        return self.title
    
    @property
    def has_cta(self):
        return bool(self.call_to_action_text and self.call_to_action_url)
