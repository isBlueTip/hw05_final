from django.db import models
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    # group name
    title = models.CharField(max_length=200)
    # group's unique address
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор публикации',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='группа, к которой будет относиться пост',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        verbose_name='картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пост, к которому оставлен комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        max_length=350,
        verbose_name='комментарий к посту',
        help_text='Напишите свой комментарий',
    )
