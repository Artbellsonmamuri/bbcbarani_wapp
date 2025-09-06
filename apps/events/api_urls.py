from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'events', api_views.EventViewSet)
router.register(r'categories', api_views.EventCategoryViewSet)
router.register(r'registrations', api_views.EventRegistrationViewSet)
router.register(r'attendance', api_views.EventAttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('calendar/', api_views.calendar_events, name='calendar'),
]
