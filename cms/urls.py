"""
Bible Baptist Church CMS - URL Configuration
Complete URL routing for all content types
"""
from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),
    
    # Pages
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    
    # Blog/Posts
    path('blog/', views.post_list, name='post_list'),
    path('blog/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),
    
    # Ministries
    path('ministries/', views.ministry_list, name='ministry_list'),
    path('ministries/<slug:slug>/', views.ministry_detail, name='ministry_detail'),
]
