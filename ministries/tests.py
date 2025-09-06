"""
Ministry showcases tests
"""
from django.test import TestCase, Client

class MinistriesTestCase(TestCase):
    """Test cases for ministries app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/ministries/')
        self.assertEqual(response.status_code, 200)
