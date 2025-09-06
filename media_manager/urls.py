"""
Media library management URL configuration
"""
from django.urls import path
from . import views

app_name = 'media_manager'

urlpatterns = [
    path('', views.index, name='index'),
]
