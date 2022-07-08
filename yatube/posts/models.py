from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreateModel

User = get_user_model()

POST_TEXT_LIMIT: int = 15


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200)
    slug = models.SlugField('url-адрес', unique=True)
    description = models.TextField('Описание группы')

    class Meta:
        ordering = ('title',)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста", help_text='Текст нового поста')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Группа, к которой относится пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        db_index=True,
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Пост',
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:POST_TEXT_LIMIT]


class Comment(CreateModel):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE
    )
    text = models.TextField('Текст комментария')

    class Meta:
        verbose_name = 'Комментарий',
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
