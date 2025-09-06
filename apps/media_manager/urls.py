from django.urls import path
from . import views

app_name = 'media_manager'

urlpatterns = [
    path('library/', views.MediaLibraryView.as_view(), name='library'),
    path('upload/', views.media_upload, name='upload'),
    path('bulk-upload/', views.MediaBulkUploadView.as_view(), name='bulk_upload'),
    path('<int:media_id>/', views.media_detail, name='detail'),
    path('<int:media_id>/delete/', views.media_delete, name='delete'),
]
