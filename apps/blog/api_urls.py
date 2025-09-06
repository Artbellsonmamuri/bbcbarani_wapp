from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'posts', api_views.BlogPostViewSet)
router.register(r'categories', api_views.BlogCategoryViewSet)
router.register(r'comments', api_views.CommentViewSet)
router.register(r'subscribers', api_views.BlogSubscriberViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
