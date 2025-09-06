"""
Ministry showcases URL configuration
"""
from django.urls import path
from . import views

app_name = 'ministries'

urlpatterns = [
    path('', views.index, name='index'),
]
