"""
Blog system with comments API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='blog_api_status'),
]
