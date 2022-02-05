from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Mikhan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое сообщение длинной более 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Checking models' __str__ method."""
        models_str_data = {
            PostModelTest.group: 'Тестовая группа',
            PostModelTest.post: 'Тестовое сообще',
        }

        for model, text in models_str_data.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), text)
