from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'notifications', api_views.NotificationViewSet)
router.register(r'preferences', api_views.NotificationPreferenceViewSet)
router.register(r'banners', api_views.AnnouncementBannerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send/', api_views.send_notification, name='send'),
    path('bulk-send/', api_views.bulk_send_notification, name='bulk_send'),
]
