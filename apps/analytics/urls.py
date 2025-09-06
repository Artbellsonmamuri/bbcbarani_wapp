from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard views
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),

    # API endpoints
    path('api/overview/', views.analytics_api_overview, name='api_overview'),
    path('api/user-summary/', views.user_analytics_summary, name='api_user_summary'),

    # Tracking endpoints
    path('track/page-view/', views.track_page_view, name='track_page_view'),
]
