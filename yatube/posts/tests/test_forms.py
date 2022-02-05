import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create(username='Nikitka')
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
            group=cls.group_1
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorised_client_1 = Client()
        self.authorised_client_1.force_login(FormsViewsTests.user_1)

    def test_create_post(self):
        """Checking creation of a new post from posts:create View."""
        num_of_posts = FormsViewsTests.group_1.posts.count()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Текст поста чтоб ещё длиннее',
            'group': FormsViewsTests.group_1.pk,
            'image': uploaded,
        }

        response = self.authorised_client_1.post(
            path=reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': FormsViewsTests.user_1.username}),
        )
        self.assertEqual(
            FormsViewsTests.group_1.posts.count(),
            num_of_posts + 1
        )

        created_post = Post.objects.get(pk=2)

        # Check newly created post's content
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group, FormsViewsTests.group_1)
        self.assertEqual(created_post.author, FormsViewsTests.user_1)
        self.assertEqual(created_post.image, 'posts/small.gif')

    def test_edit_post(self):
        """Checking editing of a new post from posts:create View."""
        new_form_data = {
            'text': 'Текст поста чтоб ещё длиннее длинного',
            'group': FormsViewsTests.group_2.pk,
        }

        response = self.authorised_client_1.post(
            path=reverse(
                'posts:post_edit',
                kwargs={'post_id': FormsViewsTests.post_with_group.pk}
            ),
            data=new_form_data,
            follow=True,
        )

        self.assertEqual(
            Post.objects.get(pk=1).text,
            new_form_data['text'],
        )
        self.assertEqual(
            str(Post.objects.get(pk=1).group),
            FormsViewsTests.group_2.title,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': 1},
        ))
