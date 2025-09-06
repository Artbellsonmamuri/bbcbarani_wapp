from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from apps.media_manager.models import Media

User = get_user_model()


class BlogCategory(models.Model):
    """Categories for organizing blog posts"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff")
    icon = models.CharField(max_length=50, blank=True)

    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Blog Category')
        verbose_name_plural = _('Blog Categories')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """Blog posts and news articles"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]

    # Basic information
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(max_length=500, help_text="Brief summary for previews")
    content = RichTextUploadingField()

    # Media
    featured_image = models.ForeignKey(Media, on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='featured_blog_posts',
                                     limit_choices_to={'media_type': 'image'})

    # Organization
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    # Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_date = models.DateTimeField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    sticky = models.BooleanField(default=False, help_text="Keep at top of blog list")

    # Comments
    allow_comments = models.BooleanField(default=True)
    comments_require_approval = models.BooleanField(default=True)

    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    og_image = models.ForeignKey(Media, on_delete=models.SET_NULL, blank=True, null=True,
                               related_name='blog_og_images',
                               limit_choices_to={'media_type': 'image'})

    # Author information
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    co_authors = models.ManyToManyField(User, blank=True, related_name='co_authored_posts')

    # Statistics
    view_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-created_at']
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-set published_date when status changes to published
        if self.status == 'published' and not self.published_date:
            from django.utils import timezone
            self.published_date = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def comment_count(self):
        return self.comments.filter(status='approved').count()

    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        import re
        word_count = len(re.findall(r'\w+', self.content))
        return max(1, round(word_count / 200))  # Average 200 words per minute


class Comment(models.Model):
    """Comments on blog posts"""

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('spam', 'Marked as Spam'),
    ]

    # Comment details
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)

    # Author (can be guest or registered user)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    guest_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_website = models.URLField(blank=True)

    # Moderation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                                   related_name='moderated_comments')
    moderated_at = models.DateTimeField(blank=True, null=True)

    # Threading (replies to comments)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    # Technical
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return f"Comment on {self.blog_post.title} by {self.get_author_name()}"

    def get_author_name(self):
        """Get display name for comment author"""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.guest_name or "Anonymous"

    def get_author_email(self):
        """Get email for comment author"""
        if self.user:
            return self.user.email
        return self.guest_email

    @property
    def is_guest_comment(self):
        return self.user is None

    def can_be_edited_by(self, user):
        """Check if user can edit this comment"""
        if user.is_admin:
            return True
        if self.user and self.user == user:
            return True
        return False


class BlogPostView(models.Model):
    """Track blog post views for analytics"""

    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True)
    referer = models.URLField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Blog Post View')
        verbose_name_plural = _('Blog Post Views')

    def __str__(self):
        return f"View of {self.blog_post.title}"


class BlogSubscriber(models.Model):
    """Email subscribers for blog updates"""

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)

    # Subscription preferences
    categories = models.ManyToManyField(BlogCategory, blank=True)
    frequency = models.CharField(max_length=20, choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Summary'),
    ], default='immediate')

    # Status
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)

    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True)
    last_email_sent = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('Blog Subscriber')
        verbose_name_plural = _('Blog Subscribers')

    def __str__(self):
        return f"{self.name or 'Subscriber'} ({self.email})"
