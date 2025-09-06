from django.urls import path
from . import views

app_name = 'prayer'

urlpatterns = [
    # Public views
    path('submit/', views.submit_prayer_request, name='submit'),
    path('wall/', views.prayer_wall, name='wall'),
    path('testimony/', views.submit_testimony, name='submit_testimony'),

    # Admin views
    path('admin/', views.prayer_admin_dashboard, name='admin_dashboard'),
    path('admin/requests/', views.PrayerRequestListView.as_view(), name='admin_list'),
    path('admin/requests/<int:request_id>/', views.prayer_request_detail, name='admin_detail'),
]
