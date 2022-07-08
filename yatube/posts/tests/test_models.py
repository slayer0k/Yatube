from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.POST_TEXT_LIMIT: int = 15

    def test_models_have_correct_object_name(self):
        '''Проеверяем соответсвие вывода __str__.'''
        expected_object_name = (
            (self.post.text[:self.POST_TEXT_LIMIT], str(self.post)),
            (self.group.title, str(self.group)),)
        for object, expected in expected_object_name:
            with self.subTest(object=object):
                self.assertEqual(object, expected)

    def test_fields_have_correct_verbose_name(self):
        '''Проверяем корректность help_text'''
        field_verbose_name = (
            ('text', 'Текст поста'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа'),
            ('image', 'Картинка')
        )
        for value, expected in field_verbose_name:
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_fields_have_correct_help_text(self):
        '''Проверяем корректность help_text'''
        field_help_text = (
            ('text', 'Текст нового поста'),
            ('group', 'Группа, к которой относится пост')
        )
        for value, expected in field_help_text:
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text,
                    expected
                )
