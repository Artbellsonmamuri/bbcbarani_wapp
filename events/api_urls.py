"""
Event calendar and RSVP API URL configuration  
"""
from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.api_status, name='events_api_status'),
]
