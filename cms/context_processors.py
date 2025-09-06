"""
Bible Baptist Church CMS - Context Processors
Provides global template variables for church information
"""
from django.conf import settings

def church_info(request):
    """
    Add church information and settings to template context
    """
    return {
        'CHURCH_NAME': getattr(settings, 'CHURCH_NAME', 'Bible Baptist Church Barani'),
        'CHURCH_ADDRESS': getattr(settings, 'CHURCH_ADDRESS', ''),
        'CHURCH_PHONE': getattr(settings, 'CHURCH_PHONE', ''),
        'CHURCH_EMAIL': getattr(settings, 'CHURCH_EMAIL', ''),
        'FACEBOOK_URL': getattr(settings, 'FACEBOOK_URL', ''),
        'TWITTER_URL': getattr(settings, 'TWITTER_URL', ''),
        'YOUTUBE_URL': getattr(settings, 'YOUTUBE_URL', ''),
        'INSTAGRAM_URL': getattr(settings, 'INSTAGRAM_URL', ''),
        'SITE_ID': getattr(settings, 'SITE_ID', 1),
        'DEBUG': getattr(settings, 'DEBUG', False),
    }
