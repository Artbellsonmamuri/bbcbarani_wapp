from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'ministries', api_views.MinistryViewSet)
router.register(r'ministry-categories', api_views.MinistryCategoryViewSet)
router.register(r'ministry-members', api_views.MinistryMemberViewSet)
router.register(r'ministry-events', api_views.MinistryEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
