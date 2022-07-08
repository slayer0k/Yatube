from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовый текст',
            group=cls.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(self.user)
        cache.clear()

    def test_posts_namespace(self):
        '''Проверка: namespace приложения posts'''
        url_reverse = (
            ('/', reverse('posts:index')),
            (
                f'/group/{self.post.group.slug}/',
                reverse('posts:group_list', args=(self.post.group.slug,))
            ),
            (
                f'/profile/{self.post.author.username}/',
                reverse('posts:profile', args=(self.post.author.username,))
            ),
            (
                f'/posts/{self.post.pk}/',
                reverse('posts:post', args=(self.post.pk,))
            ),
            ('/create/', reverse('posts:post_create')),
            (
                f'/posts/{self.post.pk}/edit',
                reverse('posts:post_edit', args=(self.post.pk,))
            ),
        )
        for url, reverse_url in url_reverse:
            with self.subTest(url=url):
                self.assertEqual(url, reverse_url)

    def test_url_redirect_anonymous_on_admin_login(self):
        '''Страница /create/ перенаправляет анонимного пользователя
        на страницу авторизации.
        '''
        response = self.guest_client.get(
            reverse('posts:post_create'),
            follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/create/'),
        )

    def test_pages_access(self):
        '''Проверка доступности страниц'''
        url_tuple = (
            (reverse('posts:index'), HTTPStatus.OK, False),
            (
                reverse('posts:group_list', args=(self.post.group.slug,)),
                HTTPStatus.OK, False
            ),
            (
                reverse('posts:profile', args=(self.post.author.username,)),
                HTTPStatus.OK, False
            ),
            (
                reverse('posts:post', args=(self.post.pk,)),
                HTTPStatus.OK, False
            ),
            (reverse('posts:post_create'), HTTPStatus.OK, True),
            (
                reverse('posts:post_edit', args=(self.post.pk,)),
                HTTPStatus.OK, True
            ),
            ('/unexisted_page/', HTTPStatus.NOT_FOUND, False),

        )
        for url, status, access in url_tuple:
            with self.subTest(url=url):
                if access:
                    response = self.author.get(url)
                else:
                    response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_post_edit_allowed_only_to_author(self):
        '''
        Страница редактирования поста доступна только автору
        '''
        url = reverse('posts:post_edit', args=(self.post.pk,))
        redirect_url = reverse('posts:post', args=(self.post.pk,))
        self.author.force_login(User.objects.create_user(username='Mao'))
        response = self.author.get(url)
        self.assertRedirects(response, redirect_url)
        response = self.guest_client.get(url)
        self.assertRedirects(response, redirect_url)

    def test_correct_templates(self):
        '''URL-адрес использует соответствующий шаблон'''
        templates_url_names = (
            (reverse('posts:index'), 'posts/index.html'),
            (
                reverse('posts:group_list', args=(self.post.group.slug,)),
                'posts/group_list.html'),
            (
                reverse('posts:profile', args=(self.post.author.username,)),
                'posts/profile.html'),
            (
                reverse('posts:post', args=(self.post.pk,)),
                'posts/post_detail.html'),
            (
                reverse('posts:post_edit', args=(self.post.pk,)),
                'posts/create_post.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
        )
        for url, template in templates_url_names:
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertTemplateUsed(response, template)

    def test_add_comment_redirect(self):
        '''Гостя перенаправляет на страницу авторизации'''
        response = self.guest_client.get(
            reverse(('posts:add_comment'), args=(self.post.pk,)), follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
