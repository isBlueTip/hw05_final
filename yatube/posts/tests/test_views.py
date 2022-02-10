import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..models import Group, Post, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

import logging  # TODO delete logger before final commit
logging.basicConfig(level=logging.DEBUG,
                    filename='test_views.log',
                    format='%(asctime)s | %(levelname)s | %(message)s')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user_1 = User.objects.create(username='Nikitka')
        cls.user_2 = User.objects.create(username='Dyusha')
        cls.group_1 = Group.objects.create(
            title='Группа №16',
            description='Описание тестовой группы'
        )
        cls.group_2 = Group.objects.create(
            title='Группа №17',
            description='Описание тестовой группы второй'
        )
        cls.post_with_group = Post.objects.create(
            text='Текст поста чтоб подлиннее',
            author=cls.user_1,
            group=cls.group_1,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client_1 = Client()
        self.authorised_client_1.force_login(PostsViewsTests.user_1)
        self.authorised_client_2 = Client()
        self.authorised_client_2.force_login(PostsViewsTests.user_2)
        cache.clear()

    def test_posts_views_use_correct_templates(self):
        """Checking correct templates usage of 'posts' app."""
        templates_namespaces_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'pk': 'gruppa-16'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'Nikitka'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in templates_namespaces_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post_page_show_correct_context(self):
        """Checking if posts:post_create is rendered with correct context."""
        response = self.authorised_client_1.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_page_creates_new_DB_instance(self):
        """Checking if POST method for posts:post_create creates
        new database instance."""

        data = {
            'text': 'Текст поста чтоб подлиннее',
            'group': 1,
            'image': PostsViewsTests.small_gif,
        }

        num_of_posts = Post.objects.count()
        self.authorised_client_1.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )

        self.assertEqual(Post.objects.count(), num_of_posts + 1)

    def test_edit_post_page_show_correct_context(self):
        """Checking if posts:post_edit is rendered with correct context."""
        response = self.authorised_client_1.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': '1'}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_pages_with_multiple_posts_show_1_post(self):
        """Checking if correct number of posts is rendered on templates
        with multiple posts."""
        pages_with_multiple_posts = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'pk': 'gruppa-16'}),
            reverse('posts:profile', kwargs={'username': 'Nikitka'}),
        ]

        for page in pages_with_multiple_posts:
            with self.subTest(page=page):
                response = self.authorised_client_1.get(page)
                self.assertEqual(len(response.context['page_obj']), 1)

    def test_group_page_without_posts_shows_0_post(self):
        """Checking if correct number of posts is rendered on templates
        with multiple posts."""
        response = self.authorised_client_1.get(reverse(
            'posts:group_list', kwargs={'pk': 'gruppa-17'}
        ))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_pages_with_multiple_posts_show_correct_context(self):
        """Checking if correct context is rendered on templates
        with multiple posts."""
        pages_with_multiple_posts = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'pk': 'gruppa-16'}),
            reverse('posts:profile', kwargs={'username': 'Nikitka'}),
        ]

        for address in pages_with_multiple_posts:
            with self.subTest(adress=address):
                response = self.authorised_client_1.get(address)
                first_post = response.context['page_obj'][0]
                post_text = first_post.text
                post_author = first_post.author
                post_group = first_post.group
                post_image = first_post.image
                self.assertEqual(post_text,
                                 PostsViewsTests.post_with_group.text)
                self.assertEqual(post_author,
                                 PostsViewsTests.post_with_group.author)
                self.assertEqual(post_group,
                                 PostsViewsTests.post_with_group.group)
                self.assertEqual(post_image,
                                 'posts/small.gif')

    def test_post_details_page_show_correct_context(self):
        """Checking if correct context is rendered
        on a post details template"""
        response = self.authorised_client_1.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': '1'}
        ))
        post = response.context['post']
        post_text = post.text
        post_author = post.author
        post_group = post.group
        post_image = post.image
        self.assertEqual(post_text, PostsViewsTests.post_with_group.text)
        self.assertEqual(post_author, PostsViewsTests.post_with_group.author)
        self.assertEqual(post_group, PostsViewsTests.post_with_group.group)
        self.assertEqual(post_image, 'posts/small.gif')

    def test_index_cache(self):
        """Checking if posts:index page is cached"""
        initial_response = self.guest_client.get(
            path=reverse('posts:index')
        )
        initial_content = initial_response.content

        Post.objects.create(
            text='тест кеширования',
            author=PostsViewsTests.user_1,
            group=PostsViewsTests.group_1,
        )

        cached_response = self.guest_client.get(
            path=reverse('posts:index')
        )
        cached_content = cached_response.content

        self.assertEqual(initial_content, cached_content)

        cache.clear()

        new_response = self.guest_client.get(
            path=reverse('posts:index')
        )
        new_content = new_response.content

        self.assertNotEqual(cached_content, new_content)

    def test_authorised_can_follow(self):
        """Checking if an authorised user is able
         to follow a post author"""
        following_before = Follow.objects.count()
        self.authorised_client_2.get(
            path=reverse(
                'posts:profile_follow',
                kwargs={'username': PostsViewsTests.user_1.username}
            )
        )

        following_after = Follow.objects.count()
        self.assertEqual(following_before + 1, following_after)

    def test_authorised_can_unfollow(self):
        """Checking if an authorised user is able
         to unfollow a following author"""
        self.authorised_client_2.get(
            path=reverse(
                'posts:profile_follow',
                kwargs={'username': PostsViewsTests.user_1.username}
            )
        )
        followings_before = Follow.objects.count()
        self.authorised_client_2.get(
            path=reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostsViewsTests.user_1.username}
            )
        )

        followings_after = Follow.objects.count()
        self.assertEqual(followings_before - 1, followings_after)

    def test_follow_index(self):
        """Checking if an authorised user is able
         to watch their followings on 'posts:follow_index'"""
        # initial number of posts on user_2's follow_index
        response = self.authorised_client_2.get(
            path=reverse('posts:follow_index')
        )
        context = response.context
        initial_posts_num = len(context['page_obj'])
        self.assertEqual(initial_posts_num, 0)
        # follow user_1
        self.authorised_client_2.get(
            path=reverse(
                'posts:profile_follow',
                kwargs={'username': PostsViewsTests.user_1.username}
            )
        )
        # user_1's post is in user_2's follow_index
        response = self.authorised_client_2.get(
            path=reverse('posts:follow_index')
        )
        context = response.context
        logging.debug('***********context***********')
        logging.debug(context['page_obj'][0])
        logging.debug(PostsViewsTests.post_with_group)

        self.assertEqual(len(context['page_obj']), initial_posts_num + 1)
        self.assertEqual(context['page_obj'][0], PostsViewsTests.post_with_group)

        response = self.authorised_client_1.get(
            path=reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create(username='Nikitka')
        cls.group_1 = Group.objects.create(
            title='Группа №16',
            description='Описание тестовой группы'
        )
        for index in range(0, 15):
            Post.objects.create(
                text=f'{index}',
                author=cls.user_1,
                group=cls.group_1
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client_1 = Client()
        self.authorised_client_1.force_login(PaginatorViewsTests.user_1)

    def test_pages_with_multiple_posts_show_10_posts_per_page(self):
        """Checking if the correct number of posts on templates
        with multiple posts are rendered on a singe page."""
        pages_with_multiple_posts = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'pk': 'gruppa-16'}),
            reverse('posts:profile', kwargs={'username': 'Nikitka'}),
        ]

        for page in pages_with_multiple_posts:
            with self.subTest(page=page):
                response = self.authorised_client_1.get(page, {'page': 2})
                self.assertEqual(len(response.context['page_obj']), 5)


class CommentsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create(username='Nikitka')
        cls.user_2 = User.objects.create(username='Dyusha')
        cls.group_1 = Group.objects.create(
            title='Группа №16',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            text='Текст поста для проверки комментариев под ним',
            author=cls.user_1,
            group=cls.group_1,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client_1 = Client()
        self.authorised_client_1.force_login(CommentsViewsTests.user_1)
        self.authorised_client_2 = Client()
        self.authorised_client_2.force_login(CommentsViewsTests.user_2)

    def test_comment_only_authorised(self):
        """Checking that only an authorised user can leave
        a comment under a post."""
        response = self.guest_client.post(
            path=reverse(
                'posts:add_comment',
                kwargs={'post_id': 1},

            ),
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')

    def test_new_comment_is_rendered_correctly(self):
        """Checking that created comments are shown
        on a post detail page."""

        data = {
            'text': 'Тестовый текст комментария',
        }

        self.authorised_client_2.post(
            path=reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentsViewsTests.post.pk},
            ),
            data=data,
            follow=True,
        )

        response = self.guest_client.get(
            path=reverse(
                'posts:post_detail',
                kwargs={'post_id': CommentsViewsTests.post.pk},
            ),
        )

        self.assertEqual(response.context['comments'][0].text, data['text'])
        self.assertEqual(
            response.context['comments'][0].author,
            CommentsViewsTests.user_2,
        )
