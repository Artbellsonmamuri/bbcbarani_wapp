from django.urls import path
from . import views

app_name = 'themes'

urlpatterns = [
    # Admin theme management
    path('editor/', views.theme_editor, name='editor'),
    path('create/', views.create_theme, name='create'),
    path('<int:theme_id>/edit/', views.edit_theme, name='edit'),
    path('<int:theme_id>/activate/', views.activate_theme, name='activate'),
    path('<int:theme_id>/preview/', views.theme_preview, name='preview'),
    path('save-settings/', views.save_theme_settings, name='save_settings'),

    # User customization
    path('customize/', views.user_theme_customization, name='user_customization'),

    # CSS delivery
    path('active.css', views.get_active_theme_css, name='active_css'),
]
