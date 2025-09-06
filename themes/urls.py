"""
Theme and CSS management URL configuration
"""
from django.urls import path
from . import views

app_name = 'themes'

urlpatterns = [
    path('', views.index, name='index'),
]
