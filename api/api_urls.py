"""
Centralized API configuration API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='api_api_status'),
]
