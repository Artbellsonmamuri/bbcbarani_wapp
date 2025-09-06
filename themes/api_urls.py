"""
Theme and CSS management API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='themes_api_status'),
]
