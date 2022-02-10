from django.test import TestCase, Client


class CoreViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_custom_templates(self):
        """Checking correct custom error templates usage."""
        custom_error_templates = {
            'random_url': 'core/404.html',
        }
        for address, template in custom_error_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
