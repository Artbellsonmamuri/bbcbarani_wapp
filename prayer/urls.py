"""
Prayer request system URL configuration
"""
from django.urls import path
from . import views

app_name = 'prayer'

urlpatterns = [
    path('', views.index, name='index'),
]
