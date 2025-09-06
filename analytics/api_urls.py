"""
Site analytics tracking API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='analytics_api_status'),
]
