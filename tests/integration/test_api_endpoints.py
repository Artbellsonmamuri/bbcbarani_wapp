"""
API endpoint integration tests
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.blog.models import BlogPost, Category
from apps.events.models import Event
from apps.ministries.models import Ministry
from apps.prayer.models import PrayerRequest

User = get_user_model()


class APIEndpointTest(TestCase):
    """Test all API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            role='Super Admin',
            is_staff=True,
            is_superuser=True
        )

        self.member_user = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='memberpass123',
            role='Member'
        )

    def test_authentication_endpoints(self):
        """Test authentication API endpoints"""
        # Test login endpoint
        response = self.client.post('/api/auth/login/', {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        # Test logout endpoint
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cms_api_endpoints(self):
        """Test CMS API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Test content sections list
        response = self.client.get('/api/cms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test content section creation
        response = self.client.post('/api/cms/', {
            'section_type': 'who_we_are',
            'title': 'Test Section',
            'body': 'Test content'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_blog_api_endpoints(self):
        """Test blog API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Create category
        category = Category.objects.create(name='Test Category', slug='test-category')

        # Test blog post creation
        response = self.client.post('/api/blog/', {
            'title': 'Test Blog Post',
            'content': 'Test content',
            'category': category.id,
            'status': 'published'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test blog post list
        response = self.client.get('/api/blog/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_events_api_endpoints(self):
        """Test events API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Test event creation
        response = self.client.post('/api/events/', {
            'title': 'Test Event',
            'description': 'Test event description',
            'start_datetime': '2024-12-25T10:00:00Z',
            'end_datetime': '2024-12-25T12:00:00Z',
            'location': 'Church Hall',
            'rsvp_required': True
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test events list
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ministries_api_endpoints(self):
        """Test ministries API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Test ministry creation
        response = self.client.post('/api/ministries/', {
            'title': 'Test Ministry',
            'description': 'Test ministry description',
            'icon': 'fas fa-heart'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test ministries list
        response = self.client.get('/api/ministries/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_prayer_requests_api(self):
        """Test prayer requests API"""
        # Test public submission (no authentication required)
        response = self.client.post('/api/prayer/', {
            'requester_name': 'John Doe',
            'email': 'john@test.com',
            'message': 'Please pray for my family.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test admin access to prayer requests
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/prayer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test member cannot access prayer requests list
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get('/api/prayer/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_media_api_endpoints(self):
        """Test media API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Test media list
        response = self.client.get('/api/media/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notifications_api_endpoints(self):
        """Test notifications API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Test notifications list
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test notification count
        response = self.client.get('/api/notifications/count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)

    def test_themes_api_endpoints(self):
        """Test themes API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Test themes list
        response = self.client.get('/api/themes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_analytics_api_endpoints(self):
        """Test analytics API endpoints"""
        self.client.force_authenticate(user=self.admin_user)

        # Test page view tracking
        response = self.client.post('/api/analytics/track-page-view/', {
            'url': 'http://testserver/',
            'path': '/',
            'title': 'Home Page',
            'user_agent': 'Test Agent'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test event tracking
        response = self.client.post('/api/analytics/track-event/', {
            'event_name': 'test_event',
            'event_data': {'key': 'value'}
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_permissions(self):
        """Test API permission controls"""
        # Test unauthenticated access
        response = self.client.get('/api/cms/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test member permissions
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get('/api/cms/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test admin permissions
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/cms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_pagination(self):
        """Test API pagination"""
        self.client.force_authenticate(user=self.admin_user)

        # Create multiple blog posts
        category = Category.objects.create(name='Test', slug='test')
        for i in range(25):
            BlogPost.objects.create(
                title=f'Post {i}',
                content=f'Content {i}',
                author=self.admin_user,
                category=category,
                status='published'
            )

        # Test pagination
        response = self.client.get('/api/blog/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 20)  # Default page size

    def test_api_filtering(self):
        """Test API filtering capabilities"""
        self.client.force_authenticate(user=self.admin_user)

        # Create blog posts with different categories
        cat1 = Category.objects.create(name='Category 1', slug='cat1')
        cat2 = Category.objects.create(name='Category 2', slug='cat2')

        BlogPost.objects.create(
            title='Post 1', content='Content 1', 
            author=self.admin_user, category=cat1, status='published'
        )
        BlogPost.objects.create(
            title='Post 2', content='Content 2', 
            author=self.admin_user, category=cat2, status='published'
        )

        # Test category filtering
        response = self.client.get('/api/blog/', {'category': cat1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Post 1')
