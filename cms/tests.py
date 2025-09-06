"""
Core content management tests
"""
from django.test import TestCase, Client

class CmsTestCase(TestCase):
    """Test cases for cms app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/cms/')
        self.assertEqual(response.status_code, 200)
