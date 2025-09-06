"""
User authentication and profiles tests
"""
from django.test import TestCase, Client
from django.urls import reverse

class AccountsTestCase(TestCase):
    """Test cases for accounts app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, 200)

    def test_api_status(self):
        """Test API status endpoint"""
        response = self.client.get('/api/accounts/status/')
        self.assertEqual(response.status_code, 200)
