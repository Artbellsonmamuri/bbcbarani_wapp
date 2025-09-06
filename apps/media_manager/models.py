from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os

User = get_user_model()


class MediaCategory(models.Model):
    """Categories for organizing media files"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Media Category')
        verbose_name_plural = _('Media Categories')
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name


class Media(models.Model):
    """Centralized media management for images, videos, documents"""

    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='media/%Y/%m/%d/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)

    # Image specific fields
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alternative text for images")
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)

    # Organizational
    category = models.ForeignKey(MediaCategory, on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    # Metadata
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)

    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)

    # Access control
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    is_public = models.BooleanField(default=True, help_text="Can be used in public content")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Media File')
        verbose_name_plural = _('Media Files')

    def __str__(self):
        return self.title or self.original_filename

    def save(self, *args, **kwargs):
        # Set original filename and file size
        if self.file:
            self.original_filename = self.file.name
            self.file_size = self.file.size

            # Determine media type based on file extension
            file_extension = os.path.splitext(self.file.name)[1].lower()

            if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                self.media_type = 'image'
            elif file_extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                self.media_type = 'video'
            elif file_extension in ['.mp3', '.wav', '.ogg', '.m4a']:
                self.media_type = 'audio'
            else:
                self.media_type = 'document'

        super().save(*args, **kwargs)

        # Get image dimensions for images
        if self.media_type == 'image' and self.file:
            try:
                with Image.open(self.file.path) as img:
                    self.width, self.height = img.size
                    # Save without calling save() again to avoid recursion
                    Media.objects.filter(pk=self.pk).update(width=self.width, height=self.height)
            except:
                pass

    @property
    def file_size_human(self):
        """Return human readable file size"""
        if not self.file_size:
            return "Unknown"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    @property
    def is_image(self):
        return self.media_type == 'image'

    @property
    def is_video(self):
        return self.media_type == 'video'

    def get_thumbnail_url(self):
        """Get thumbnail URL for display purposes"""
        if self.is_image:
            return self.file.url
        elif self.is_video:
            # Return placeholder for video thumbnail
            return '/static/images/video-thumbnail.png'
        else:
            return '/static/images/document-icon.png'


class MediaUsage(models.Model):
    """Track where media files are being used"""
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='usage_instances')
    content_type = models.CharField(max_length=50)  # 'content_section', 'blog_post', etc.
    object_id = models.PositiveIntegerField()
    field_name = models.CharField(max_length=50)  # Which field is using this media
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Media Usage')
        verbose_name_plural = _('Media Usage')
        unique_together = ['media', 'content_type', 'object_id', 'field_name']

    def __str__(self):
        return f"{self.media.title} used in {self.content_type} #{self.object_id}"
