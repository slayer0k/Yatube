import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='test text',
            image=cls.uploaded
        )
        cls.other_group = Group.objects.create(
            title='Test group 2',
            slug='test-slug-2',
            description='test description',
        )
        cls.second_user = User.objects.create_user(username='Mao')

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        caches['default'].clear()

    def test_pages_has_right_context_create(self):
        '''Проверка передачи правильного контекста в форму'''
        reverse_tuple = (
            (reverse('posts:post_create'), False),
            (reverse('posts:post_edit', args=(self.post.pk,)), True)
        )
        for url, edit in reverse_tuple:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIsInstance(
                    response.context['form'],
                    PostForm
                )
                if edit:
                    self.assertEqual(
                        self.post,
                        response.context['form'].instance
                    )

    def test_index_profile_group_page_show_correct_context(self):
        '''Проверка: новый пост находится на соответствующих страницах и
        отсутствует на странице другой группы
        '''
        url_reverse = (
            reverse('posts:index'),
            reverse('posts:profile', args=(self.post.author.username,)),
            reverse(
                'posts:group_list', args=(self.post.group.slug,)
            ),
        )
        for url in url_reverse:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIn(self.post, response.context['page_obj'])

        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.other_group.slug,))
        )
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_post_detail_shows_correct_context(self):
        '''Проверка post_detail получает соотвествующий контекст'''
        response = self.guest_client.get(
            reverse('posts:post', args=(self.post.pk,))
        )
        self.assertEqual(response.context['post'], self.post)

    def test_group_context(self):
        '''Проверка: на страницу /group/ передаётся группа'''
        response = self.guest_client.get(
            reverse('posts:group_list', args=(self.post.group.slug,))
        )
        self.assertEqual(self.post.group, response.context['group'])

    def test_profile_context(self):
        '''
        Проверка: на страницу /profile/ передаётся автор и количество постов
        '''
        response = self.guest_client.get(
            reverse('posts:profile', args=(self.post.author.username,))
        )
        self.assertEqual(self.post.author, response.context['author'])
        self.assertEqual(
            response.context['count'],
            self.post.author.posts.count())

    def test_zache(self):
        """Проверка кэширования"""
        response = self.guest_client.get(
            reverse('posts:index'))
        Post.objects.create(
            author=self.user,
            group=self.group,
            text='test caches')
        self.assertEqual(
            response.content,
            self.guest_client.get(reverse('posts:index')).content
        )
        caches['default'].clear()
        self.assertNotEqual(
            response.content,
            self.guest_client.get(reverse('posts:index')).content
        )

    def test_follow(self):
        """авторизованный пользователь может подписаваться"""
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.second_user).exists()
        )
        self.authorized_client.force_login(self.second_user)
        self.authorized_client.get(
            reverse('posts:profile_follow', args=(self.user.username,))
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.user,
                user=self.second_user).exists()
        )

    def test_unfollow(self):
        """Проверка возможности отписки"""
        self.authorized_client.force_login(self.second_user)
        Follow.objects.create(
            author=self.user,
            user=self.second_user
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.user.username,))
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.second_user,
            ).exists()
        )

    def test_follow_index_context(self):
        """
        Проверка: новая запись появляется только у подписвшегося пользователя
        """
        Follow.objects.create(
            author=self.user,
            user=self.second_user
        )
        self.authorized_client.force_login(self.second_user)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.post, response.context.get('page_obj'))
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response.context.get('page_obj'))
