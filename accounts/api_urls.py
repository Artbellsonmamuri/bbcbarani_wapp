"""
User authentication and profiles API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='accounts_api_status'),
]
