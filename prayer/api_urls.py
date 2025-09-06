"""
Prayer request system API URL configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='prayer_api_status'),
]
