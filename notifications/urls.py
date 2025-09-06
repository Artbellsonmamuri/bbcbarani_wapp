"""
Real-time notifications URL configuration
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.index, name='index'),
]
