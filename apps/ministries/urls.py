from django.urls import path
from . import views

app_name = 'ministries'

urlpatterns = [
    # Public views
    path('', views.MinistryListView.as_view(), name='list'),
    path('<slug:slug>/', views.MinistryDetailView.as_view(), name='detail'),
    path('category/<slug:category_slug>/', views.ministries_by_category, name='by_category'),
    path('<int:ministry_id>/contact/', views.ministry_contact, name='contact'),
    path('<int:ministry_id>/join/', views.join_ministry, name='join'),
    path('<int:ministry_id>/leave/', views.leave_ministry, name='leave'),

    # Admin views
    path('admin/', views.MinistryAdminListView.as_view(), name='admin_list'),
]
