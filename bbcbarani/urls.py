"""
Bible Baptist Church CMS - URL Configuration
Complete working version with all apps
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'ok', 
        'service': 'Bible Baptist Church CMS',
        'version': '1.0.0'
    })

def home_redirect(request):
    """Temporary home page"""
    return JsonResponse({
        'message': 'Bible Baptist Church CMS is running!',
        'admin': '/admin/',
        'api': '/api/',
        'health': '/health/'
    })

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),

    # Admin interface
    path('admin/', admin.site.urls),

    # Temporary home page
    path('', home_redirect, name='home'),

    # API endpoints (basic structure)
    path('api/', include('api.urls', namespace='api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site configuration
admin.site.site_header = "Bible Baptist Church CMS Admin"
admin.site.site_title = "BBC CMS Admin"
admin.site.index_title = "Church Management System"
