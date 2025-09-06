"""
Prayer request system tests
"""
from django.test import TestCase, Client

class PrayerTestCase(TestCase):
    """Test cases for prayer app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/prayer/')
        self.assertEqual(response.status_code, 200)
