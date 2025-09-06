from django.urls import path
from . import views

app_name = 'media_manager'

urlpatterns = [
    # Main library views
    path('', views.MediaLibraryView.as_view(), name='library'),
    path('ajax-upload/', views.ajax_upload, name='ajax_upload'),

    # Media file views
    path('media/<int:pk>/', views.MediaDetailView.as_view(), name='detail'),
    path('media/<int:pk>/download/', views.media_download, name='download'),

    # Admin views
    path('admin/', views.media_dashboard, name='admin_dashboard'),
]
