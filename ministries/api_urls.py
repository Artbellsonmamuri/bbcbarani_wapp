"""
Ministry showcases API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='ministries_api_status'),
]
