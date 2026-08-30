from django.test import TestCase


class ChatTestCase(TestCase):
    """Test cases for chat application."""

    def test_home_page_loads(self):
        """Test that home page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
