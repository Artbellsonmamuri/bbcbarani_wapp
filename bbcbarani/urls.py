"""bbcbarani URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.api_urls')),
    path('api/', include('apps.cms.api_urls')),
    path('api/', include('apps.ministries.api_urls')),
    path('api/', include('apps.prayer.api_urls')),
    path('api/', include('apps.blog.api_urls')),
    path('api/', include('apps.events.api_urls')),
    path('api/', include('apps.themes.api_urls')),
    path('api/', include('apps.media_manager.api_urls')),
    path('api/', include('apps.notifications.api_urls')),

    # Frontend URLs
    path('', include('apps.cms.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('ministries/', include('apps.ministries.urls')),
    path('prayer/', include('apps.prayer.urls')),
    path('blog/', include('apps.blog.urls')),
    path('events/', include('apps.events.urls')),
    path('media/', include('apps.media_manager.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site configuration
admin.site.site_header = "BBC Barani CMS"
admin.site.site_title = "BBC Barani Admin"
admin.site.index_title = "Welcome to BBC Barani Content Management"
