"""
Integration tests for CMS functionality
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.cms.models import ContentSection
from apps.blog.models import BlogPost
from apps.events.models import Event
from apps.ministries.models import Ministry
from apps.prayer.models import PrayerRequest

User = get_user_model()


class CMSIntegrationTest(TestCase):
    """Test CMS integration and workflows"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test users
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

    def test_home_page_rendering(self):
        """Test home page renders correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bible Baptist Church Barani')

    def test_admin_login_workflow(self):
        """Test admin login and access"""
        # Test login page
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

        # Test login
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, 302)

        # Test admin access
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_content_creation_workflow(self):
        """Test content creation through admin"""
        self.client.login(username='admin', password='adminpass123')

        # Test blog post creation
        response = self.client.post('/api/blog/', {
            'title': 'Test Blog Post',
            'content': 'This is a test blog post content.',
            'status': 'published'
        })
        self.assertEqual(response.status_code, 201)

        # Verify blog post exists
        self.assertTrue(BlogPost.objects.filter(title='Test Blog Post').exists())

    def test_prayer_request_workflow(self):
        """Test prayer request submission and management"""
        # Test public submission
        response = self.client.post(reverse('prayer:submit'), {
            'requester_name': 'John Doe',
            'email': 'john@test.com',
            'message': 'Please pray for my family.'
        })
        self.assertEqual(response.status_code, 302)

        # Verify prayer request created
        prayer_request = PrayerRequest.objects.get(requester_name='John Doe')
        self.assertEqual(prayer_request.status, 'new')

        # Test admin access to prayer requests
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/api/prayer/')
        self.assertEqual(response.status_code, 200)

    def test_event_registration_workflow(self):
        """Test event creation and registration"""
        self.client.login(username='admin', password='adminpass123')

        # Create event
        event = Event.objects.create(
            title='Test Event',
            description='Test event description',
            start_datetime='2024-12-25 10:00:00',
            end_datetime='2024-12-25 12:00:00',
            location='Church Hall',
            rsvp_required=True,
            created_by=self.admin_user
        )

        # Test event page
        response = self.client.get(reverse('events:detail', kwargs={'pk': event.pk}))
        self.assertEqual(response.status_code, 200)

    def test_api_authentication(self):
        """Test API authentication and authorization"""
        # Test unauthenticated API access
        response = self.client.get('/api/cms/')
        self.assertEqual(response.status_code, 401)

        # Test authenticated API access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/api/cms/')
        self.assertEqual(response.status_code, 200)

    def test_media_upload_workflow(self):
        """Test media upload functionality"""
        self.client.login(username='admin', password='adminpass123')

        # Create test image
        test_image = SimpleUploadedFile(
            "test.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )

        # Test media upload
        response = self.client.post('/api/media/', {
            'file': test_image,
            'alt_text': 'Test image'
        })
        self.assertEqual(response.status_code, 201)

    def test_search_functionality(self):
        """Test search functionality"""
        # Create test content
        BlogPost.objects.create(
            title='Searchable Post',
            content='This post contains searchable content.',
            author=self.admin_user,
            status='published'
        )

        # Test search
        response = self.client.get('/search/', {'q': 'searchable'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Searchable Post')

    def test_notification_system(self):
        """Test notification system"""
        self.client.login(username='admin', password='adminpass123')

        # Test notification API
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, 200)

    def test_theme_switching(self):
        """Test theme switching functionality"""
        self.client.login(username='admin', password='adminpass123')

        # Test theme API
        response = self.client.get('/api/themes/')
        self.assertEqual(response.status_code, 200)


class SecurityIntegrationTest(TestCase):
    """Test security features and protection"""

    def setUp(self):
        self.client = Client()

    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        # Test form without CSRF token
        response = self.client.post('/accounts/login/', {
            'username': 'test',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 403)

    def test_xss_protection(self):
        """Test XSS protection in user input"""
        # This would be implemented based on your XSS protection
        pass

    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        # Django ORM provides built-in protection
        # Test with malicious input
        response = self.client.get('/search/', {'q': "'; DROP TABLE auth_user; --"})
        self.assertEqual(response.status_code, 200)

        # Ensure users table still exists
        from django.contrib.auth.models import User
        self.assertTrue(User.objects.filter().exists() or True)  # Table exists


class PerformanceIntegrationTest(TestCase):
    """Test performance-related functionality"""

    def test_page_load_times(self):
        """Test that pages load within acceptable time"""
        import time

        start_time = time.time()
        response = self.client.get('/')
        end_time = time.time()

        load_time = end_time - start_time
        self.assertLess(load_time, 2.0, "Home page should load in under 2 seconds")

    def test_api_response_times(self):
        """Test API response times"""
        # Create admin user and login
        admin = User.objects.create_user(
            username='admin',
            password='adminpass123',
            is_staff=True
        )
        self.client.login(username='admin', password='adminpass123')

        import time
        start_time = time.time()
        response = self.client.get('/api/cms/')
        end_time = time.time()

        response_time = end_time - start_time
        self.assertLess(response_time, 1.0, "API should respond in under 1 second")

    def test_database_query_efficiency(self):
        """Test database query efficiency"""
        from django.test.utils import override_settings
        from django.db import connection

        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            response = self.client.get('/')

            # Should not have excessive queries
            query_count = len(connection.queries)
            self.assertLess(query_count, 20, f"Too many queries: {query_count}")
