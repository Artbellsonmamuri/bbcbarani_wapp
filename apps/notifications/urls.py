from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # User notification views
    path('', views.notification_list, name='list'),
    path('preferences/', views.notification_preferences, name='preferences'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),

    # API endpoints
    path('api/count/', views.get_notification_count, name='api_count'),
    path('api/recent/', views.get_recent_notifications, name='api_recent'),
    path('api/banners/', views.get_active_banners, name='api_banners'),

    # Admin views
    path('admin/', views.notification_dashboard, name='admin_dashboard'),
    path('admin/send/', views.send_custom_notification, name='admin_send'),
]
