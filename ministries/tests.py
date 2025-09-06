"""
Ministry showcases tests
"""
from django.test import TestCase, Client
from django.urls import reverse

class MinistriesTestCase(TestCase):
    """Test cases for ministries app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/ministries/')
        self.assertEqual(response.status_code, 200)

    def test_api_status(self):
        """Test API status endpoint"""
        response = self.client.get('/api/ministries/status/')
        self.assertEqual(response.status_code, 200)
