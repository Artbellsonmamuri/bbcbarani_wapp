"""
URL Configuration for Bible Baptist Church Barani CMS

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve
import os

# Import sitemaps
from apps.cms.sitemaps import CMSSitemap
from apps.blog.sitemaps import BlogSitemap
from apps.events.sitemaps import EventSitemap

# Sitemap configuration
sitemaps = {
    'cms': CMSSitemap,
    'blog': BlogSitemap,
    'events': EventSitemap,
}

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Main application URLs
    path('', include('apps.cms.urls', namespace='cms')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('events/', include('apps.events.urls', namespace='events')),
    path('ministries/', include('apps.ministries.urls', namespace='ministries')),
    path('prayer/', include('apps.prayer.urls', namespace='prayer')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('media-manager/', include('apps.media_manager.urls', namespace='media_manager')),
    path('themes/', include('apps.themes.urls', namespace='themes')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),

    # API URLs
    path('api/auth/', include('apps.accounts.api_urls')),
    path('api/cms/', include('apps.cms.api_urls')),
    path('api/blog/', include('apps.blog.api_urls')),
    path('api/events/', include('apps.events.api_urls')),
    path('api/ministries/', include('apps.ministries.api_urls')),
    path('api/prayer/', include('apps.prayer.api_urls')),
    path('api/notifications/', include('apps.notifications.api_urls')),
    path('api/media/', include('apps.media_manager.api_urls')),
    path('api/themes/', include('apps.themes.api_urls')),
    path('api/analytics/', include('apps.analytics.api_urls')),

    # SEO and utilities
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', include('apps.cms.urls')),  # Handled by CMS app

    # Favicon redirect
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico', permanent=True)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Handle media files in production
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]

# Custom error handlers
handler404 = 'apps.cms.views.custom_404_view'
handler500 = 'apps.cms.views.custom_500_view'
