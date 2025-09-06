from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'prayer-requests', api_views.PrayerRequestViewSet)
router.register(r'prayer-categories', api_views.PrayerCategoryViewSet)
router.register(r'prayer-responses', api_views.PrayerResponseViewSet)
router.register(r'prayer-wall', api_views.PrayerWallViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
