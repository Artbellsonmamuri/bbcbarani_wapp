from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Public views
    path('', views.EventListView.as_view(), name='list'),
    path('calendar/', views.event_calendar, name='calendar'),
    path('<slug:slug>/', views.EventDetailView.as_view(), name='detail'),
    path('<slug:event_slug>/register/', views.register_for_event, name='register'),
    path('<slug:event_slug>/cancel/', views.cancel_registration, name='cancel_registration'),

    # Admin views
    path('admin/', views.events_admin_dashboard, name='admin_dashboard'),
    path('admin/<int:event_id>/checkin/', views.event_check_in, name='admin_checkin'),
]
