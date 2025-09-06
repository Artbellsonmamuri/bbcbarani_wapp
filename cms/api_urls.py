"""
Core content management API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='cms_api_status'),
]
