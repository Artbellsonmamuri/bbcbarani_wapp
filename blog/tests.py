"""
Blog system with comments tests
"""
from django.test import TestCase, Client

class BlogTestCase(TestCase):
    """Test cases for blog app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
