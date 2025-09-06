"""
Media library management API URL configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='media_manager_api_status'),
]
