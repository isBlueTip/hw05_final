from http import HTTPStatus

from django.test import TestCase, Client


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_location(self):
        """Checking static pages availability of 'about' app."""
        about_urls = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in about_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_urls_use_correct_template(self):
        """Checking correct templates usage of 'about' app."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
