from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostsURLsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create(username='Nikitka')
        cls.user_2 = User.objects.create(username='Dyusha')
        cls.group = Group.objects.create(
            title='Группа №16',
            description='Описание тестовой группы'
        )
        cls.post_with_group = Post.objects.create(
            text='Текст поста чтоб подлиннее',
            author=cls.user_1,
            group=cls.group
        )
        cls.post_without_group = Post.objects.create(
            text='Текст поста чтоб ещё длиннее и графоманистее первого',
            author=cls.user_1
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client_1 = Client()
        self.authorised_client_1.force_login(PostsURLsTests.user_1)
        self.authorised_client_2 = Client()
        self.authorised_client_2.force_login(PostsURLsTests.user_2)
        cache.clear()

    def test_posts_urls_exist_at_desired_location_for_unauthorised(self):
        """Checking pages availability for unauthorised users of 'post' app."""
        posts_urls_for_guest = [
            '/',
            '/profile/Nikitka/',
            '/posts/1/',
            '/group/gruppa-16/',
        ]
        for address in posts_urls_for_guest:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_and_redirects_lead_as_desired_for_authorised(self):
        """Checking pages availability for authorised users of 'post' app."""
        posts_urls_for_user = [
            '/create/',
            '/posts/1/edit/'
        ]

        for address in posts_urls_for_user:
            with self.subTest(address=address):
                response = self.authorised_client_1.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.authorised_client_2.get(posts_urls_for_user[1])
        self.assertRedirects(response, '/')

    def test_posts_redirects_route_to_desired_location_for_unauthorised(self):
        """Checking redirects for unauthorised users of 'post' app."""
        posts_urls_for_guest = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/'
        }
        for address, redirect_url in posts_urls_for_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_urls_use_correct_templates(self):
        """Checking correct templates usage of 'about' app."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/profile/Nikitka/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/group/gruppa-16/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorised_client_1.get(address)
                self.assertTemplateUsed(response, template)
