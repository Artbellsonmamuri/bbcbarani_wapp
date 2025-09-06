"""
Media library management tests
"""
from django.test import TestCase, Client
from django.urls import reverse

class MediaManagerTestCase(TestCase):
    """Test cases for media_manager app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/media_manager/')
        self.assertEqual(response.status_code, 200)

    def test_api_status(self):
        """Test API status endpoint"""
        response = self.client.get('/api/media_manager/status/')
        self.assertEqual(response.status_code, 200)
