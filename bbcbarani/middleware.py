"""
Custom middleware for bbcbarani project
"""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to enable maintenance mode
    """
    def process_request(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            if not request.user.is_staff and not request.path.startswith('/admin/'):
                return redirect('maintenance')
        return None


class ThemeMiddleware(MiddlewareMixin):
    """
    Middleware to inject current active theme into template context
    """
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            try:
                from apps.themes.models import SiteTheme
                active_theme = SiteTheme.objects.filter(is_active=True).first()
                if response.context_data is None:
                    response.context_data = {}
                response.context_data['active_theme'] = active_theme
            except:
                pass
        return response
