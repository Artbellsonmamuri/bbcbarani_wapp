"""
Site analytics tracking tests
"""
from django.test import TestCase, Client

class AnalyticsTestCase(TestCase):
    """Test cases for analytics app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/analytics/')
        self.assertEqual(response.status_code, 200)
