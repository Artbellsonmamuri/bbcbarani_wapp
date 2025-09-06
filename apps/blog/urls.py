from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Public views
    path('', views.BlogListView.as_view(), name='list'),
    path('post/<slug:slug>/', views.BlogDetailView.as_view(), name='detail'),
    path('post/<slug:post_slug>/comment/', views.add_comment, name='add_comment'),
    path('subscribe/', views.subscribe_to_blog, name='subscribe'),

    # Admin views
    path('admin/', views.blog_admin_dashboard, name='admin_dashboard'),
    path('admin/comments/', views.moderate_comments, name='moderate_comments'),
]
