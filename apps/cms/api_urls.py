from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'sections', api_views.ContentSectionViewSet)
router.register(r'welcome-screens', api_views.WelcomeScreenViewSet)
router.register(r'service-schedules', api_views.ServiceScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('seo-settings/', api_views.SEOSettingsAPIView.as_view(), name='seo-settings'),
    path('header-footer/', api_views.HeaderFooterAPIView.as_view(), name='header-footer'),
]
