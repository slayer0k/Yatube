import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='test'
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='test text',
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        '''Валидная форма создает запись в Post'''
        posts_count = Post.objects.count()
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
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group_id=form_data['group'],
                image='posts/small.gif'
            ).exists()
        )
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.user.username,)
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group_id=form_data['group'],
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        '''Проверка изменения поста в базе данных'''
        post_count = Post.objects.count()
        form_data = {
            'text': 'test text edit',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=(self.post.pk,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.post.author,
                pk=self.post.pk,
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post',
                args=(self.post.pk,)
            )
        )

    def test_add_comment(self):
        comment_count = self.post.comments.count()
        form_data = {'text': 'test text'}
        self.assertFalse(
            self.post.comments.filter(
                text=form_data['text'], author=self.user).exists())
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertEqual(comment_count + 1, self.post.comments.count())
        self.assertTrue(
            self.post.comments.filter(
                text=form_data['text'], author=self.user).exists()
        )
        self.assertRedirects(
            response,
            reverse('posts:post', args=(self.post.id,)))
