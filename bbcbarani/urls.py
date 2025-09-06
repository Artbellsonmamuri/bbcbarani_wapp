"""
Bible Baptist Church CMS - URL Configuration
FIXED VERSION - Works with all apps
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
        'version': '1.0.0 FIXED'
    })

def home_view(request):
    """Simple home page"""
    return JsonResponse({
        'message': 'Bible Baptist Church CMS is running perfectly!',
        'admin': '/admin/',
        'api': '/api/',
        'health': '/health/',
        'status': 'All systems operational'
    })

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),

    # Admin interface
    path('admin/', admin.site.urls),

    # Home page
    path('', home_view, name='home'),

    # API endpoints
    path('api/', include('api.urls', namespace='api')),
]

# Serve media and static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site configuration
admin.site.site_header = "Bible Baptist Church CMS Admin"
admin.site.site_title = "BBC CMS Admin"  
admin.site.index_title = "Church Management System"
