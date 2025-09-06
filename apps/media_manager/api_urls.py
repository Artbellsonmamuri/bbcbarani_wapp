from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'media', api_views.MediaViewSet)
router.register(r'categories', api_views.MediaCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
