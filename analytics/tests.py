"""
Site analytics tracking tests
"""
from django.test import TestCase, Client
from django.urls import reverse

class AnalyticsTestCase(TestCase):
    """Test cases for analytics app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/analytics/')
        self.assertEqual(response.status_code, 200)

    def test_api_status(self):
        """Test API status endpoint"""
        response = self.client.get('/api/analytics/status/')
        self.assertEqual(response.status_code, 200)
