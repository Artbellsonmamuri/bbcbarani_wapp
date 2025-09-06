from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('section/<str:section_type>/', views.section_detail, name='section'),
    path('who-we-are/', views.section_detail, {'section_type': 'who_we_are'}, name='who_we_are'),
    path('articles-of-faith/', views.section_detail, {'section_type': 'articles_of_faith'}, name='articles_of_faith'),
    path('salvation/', views.section_detail, {'section_type': 'call_to_salvation'}, name='salvation'),
    path('schedule/', views.section_detail, {'section_type': 'schedule'}, name='schedule'),

    # Admin content management
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/content/', views.ContentSectionListView.as_view(), name='admin_content_list'),
    path('admin/content/create/', views.ContentSectionCreateView.as_view(), name='admin_content_create'),
    path('admin/content/<int:pk>/edit/', views.ContentSectionUpdateView.as_view(), name='admin_content_edit'),
    path('admin/content/bulk-actions/', views.bulk_content_actions, name='bulk_content_actions'),
]
