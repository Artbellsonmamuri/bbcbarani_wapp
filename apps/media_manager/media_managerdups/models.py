from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.urls import reverse
from PIL import Image
import os
import uuid

User = get_user_model()


def upload_to_media(instance, filename):
    """Generate upload path for media files"""
    # Get file extension
    ext = filename.split('.')[-1]

    # Generate unique filename
    filename = f"{uuid.uuid4()}.{ext}"

    # Organize by media type and year/month
    year = timezone.now().year
    month = timezone.now().month

    media_type = instance.media_type or 'other'
    return f'media/{media_type}/{year}/{month:02d}/{filename}'


class MediaFolder(models.Model):
    """Folders for organizing media files"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    # Permissions
    is_public = models.BooleanField(default=True, help_text="Public folders are visible to all users")
    allowed_users = models.ManyToManyField(User, blank=True, related_name='media_folders')

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_folders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Media Folder')
        verbose_name_plural = _('Media Folders')
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name

    @property
    def full_path(self):
        """Get full folder path"""
        if self.parent:
            return f"{self.parent.full_path}/{self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('media_manager:folder', kwargs={'slug': self.slug})

    def can_access(self, user):
        """Check if user can access this folder"""
        if self.is_public:
            return True
        if user.is_staff:
            return True
        if user == self.created_by:
            return True
        return self.allowed_users.filter(id=user.id).exists()


class MediaFile(models.Model):
    """Media files with metadata and organization"""

    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]

    # Basic file information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=upload_to_media)

    # Metadata
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)

    # Image-specific fields
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)

    # Organization
    folder = models.ForeignKey(MediaFolder, on_delete=models.SET_NULL, blank=True, null=True, related_name='files')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")

    # SEO and accessibility
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alt text for images")
    caption = models.TextField(blank=True)

    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0, help_text="Number of times this media is used")
    last_used = models.DateTimeField(blank=True, null=True)

    # Permissions and sharing
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    copyright_info = models.CharField(max_length=255, blank=True)
    license_type = models.CharField(max_length=50, choices=[
        ('all_rights_reserved', 'All Rights Reserved'),
        ('creative_commons', 'Creative Commons'),
        ('public_domain', 'Public Domain'),
        ('church_use', 'Church Use Only'),
    ], default='church_use')

    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Media File')
        verbose_name_plural = _('Media Files')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['media_type', '-created_at']),
            models.Index(fields=['uploaded_by', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]

    def __str__(self):
        return self.title or self.original_filename

    def save(self, *args, **kwargs):
        # Auto-determine media type based on mime type
        if not self.media_type:
            self.media_type = self._determine_media_type()

        # Set original filename if not set
        if not self.original_filename and self.file:
            self.original_filename = os.path.basename(self.file.name)

        # Set file size
        if self.file and not self.file_size:
            self.file_size = self.file.size

        # Generate title from filename if not provided
        if not self.title:
            name = os.path.splitext(self.original_filename)[0]
            self.title = name.replace('_', ' ').replace('-', ' ').title()

        super().save(*args, **kwargs)

        # Process image dimensions after save
        if self.media_type == 'image' and not self.width:
            self._extract_image_dimensions()

    def _determine_media_type(self):
        """Determine media type from mime type"""
        if not self.mime_type:
            return 'other'

        if self.mime_type.startswith('image/'):
            return 'image'
        elif self.mime_type.startswith('video/'):
            return 'video'
        elif self.mime_type.startswith('audio/'):
            return 'audio'
        elif self.mime_type in ['application/pdf', 'application/msword', 'text/plain']:
            return 'document'
        elif self.mime_type in ['application/zip', 'application/x-rar-compressed']:
            return 'archive'
        else:
            return 'other'

    def _extract_image_dimensions(self):
        """Extract width and height from image files"""
        if self.media_type == 'image' and self.file:
            try:
                with Image.open(self.file.path) as img:
                    self.width, self.height = img.size
                    self.save(update_fields=['width', 'height'])
            except Exception:
                pass

    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.original_filename)[1].lower()

    @property
    def formatted_file_size(self):
        """Get human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def is_image(self):
        return self.media_type == 'image'

    @property
    def is_video(self):
        return self.media_type == 'video'

    @property
    def is_audio(self):
        return self.media_type == 'audio'

    @property
    def is_document(self):
        return self.media_type == 'document'

    @property
    def thumbnail_url(self):
        """Get thumbnail URL for the media"""
        if self.is_image:
            # In production, you'd use a thumbnail generation service
            return self.file.url
        else:
            # Return default thumbnails based on file type
            return f'/static/media_manager/icons/{self.media_type}.png'

    def get_tags_list(self):
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def get_absolute_url(self):
        return reverse('media_manager:detail', kwargs={'pk': self.pk})

    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])

    def can_access(self, user):
        """Check if user can access this media file"""
        if self.is_public:
            return True
        if user.is_staff:
            return True
        if user == self.uploaded_by:
            return True
        if self.folder and self.folder.can_access(user):
            return True
        return False

    def can_edit(self, user):
        """Check if user can edit this media file"""
        if user.is_staff:
            return True
        if user == self.uploaded_by:
            return True
        return False


class MediaCollection(models.Model):
    """Collections for grouping related media files"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    # Collection settings
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Media files in this collection
    media_files = models.ManyToManyField(MediaFile, through='MediaCollectionItem', related_name='collections')

    # Cover image
    cover_image = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='collection_covers')

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Media Collection')
        verbose_name_plural = _('Media Collections')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('media_manager:collection', kwargs={'slug': self.slug})

    @property
    def media_count(self):
        return self.media_files.count()


class MediaCollectionItem(models.Model):
    """Through model for media collection items with ordering"""

    collection = models.ForeignKey(MediaCollection, on_delete=models.CASCADE)
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    # Optional item-specific data
    caption = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)

    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order', 'added_at']
        unique_together = ('collection', 'media_file')

    def __str__(self):
        return f"{self.collection.name} - {self.media_file.title}"


class MediaUsage(models.Model):
    """Track where media files are used"""

    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='usage_records')

    # Content reference
    content_type = models.CharField(max_length=50, help_text="Type of content using this media")
    content_id = models.PositiveIntegerField(help_text="ID of content using this media")
    content_title = models.CharField(max_length=255, blank=True)
    content_url = models.URLField(blank=True)

    # Usage context
    usage_context = models.CharField(max_length=100, choices=[
        ('featured_image', 'Featured Image'),
        ('content_image', 'Content Image'),
        ('gallery', 'Gallery'),
        ('background', 'Background'),
        ('attachment', 'Attachment'),
        ('other', 'Other'),
    ], default='other')

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether this usage is still active")

    class Meta:
        verbose_name = _('Media Usage')
        verbose_name_plural = _('Media Usage Records')
        ordering = ['-created_at']
        unique_together = ('media_file', 'content_type', 'content_id', 'usage_context')

    def __str__(self):
        return f"{self.media_file.title} used in {self.content_type}"


class MediaDownload(models.Model):
    """Track media file downloads"""

    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='downloads')
    downloaded_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    # Download info
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)

    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Media Download')
        verbose_name_plural = _('Media Downloads')
        ordering = ['-downloaded_at']

    def __str__(self):
        user = self.downloaded_by.username if self.downloaded_by else 'Anonymous'
        return f"{self.media_file.title} downloaded by {user}"
