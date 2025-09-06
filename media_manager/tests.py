"""
Media library management tests
"""
from django.test import TestCase, Client

class MediaManagerTestCase(TestCase):
    """Test cases for media_manager app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/media_manager/')
        self.assertEqual(response.status_code, 200)
