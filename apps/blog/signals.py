from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import BlogPost, Comment


@receiver(post_save, sender=BlogPost)
def handle_blog_post_published(sender, instance, created, **kwargs):
    """Handle blog post publication"""

    if instance.status == 'published' and instance.published_date:
        # TODO: Send notifications to subscribers
        # TODO: Share on social media
        pass


@receiver(post_save, sender=Comment)
def handle_comment_submitted(sender, instance, created, **kwargs):
    """Handle new comment submission"""

    if created:
        # TODO: Send notification to post author
        # TODO: Send moderation notification if approval required
        pass
