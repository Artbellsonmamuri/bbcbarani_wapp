"""
Core content management URL configuration
"""
from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('', views.index, name='index'),
]
