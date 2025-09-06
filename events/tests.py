"""
Event calendar and RSVP tests
"""
from django.test import TestCase, Client

class EventsTestCase(TestCase):
    """Test cases for events app"""

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        """Test index view"""
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)
