"""
User authentication and profiles URL configuration
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
]
