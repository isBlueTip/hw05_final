from django.test import TestCase, Client  # , override_settings

# TODO delete comments


class CoreViewsTests(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     cls.user_1 = User.objects.create(username='Nikitka')
    #     cls.group_1 = Group.objects.create(
    #         title='Группа №16',
    #         description='Описание тестовой группы'
    #     )
    #     cls.group_2 = Group.objects.create(
    #         title='Группа №17',
    #         description='Описание тестовой группы второй'
    #     )
    #     cls.post_with_group = Post.objects.create(
    #         text='Текст поста чтоб подлиннее',
    #         author=cls.user_1,
    #         group=cls.group_1,
    #         image=PostsViewsTests.uploaded,
    #     )

    def setUp(self):
        self.guest_client = Client()
        # self.authorised_client_1 = Client()
        # self.authorised_client_1.force_login(PostsViewsTests.user_1)

    def test_custom_templates(self):
        """Checking correct custom error templates usage."""
        custom_error_templates = {
            'random_url': 'core/404.html',
        }
        for address, template in custom_error_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
