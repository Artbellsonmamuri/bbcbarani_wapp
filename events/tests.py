"""
Event calendar and RSVP tests
"""
from django.test import TestCase, Client
from django.urls import reverse

class EventsTestCase(TestCase):
    """Test cases for events app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)

    def test_api_status(self):
        """Test API status endpoint"""
        response = self.client.get('/api/events/status/')
        self.assertEqual(response.status_code, 200)
