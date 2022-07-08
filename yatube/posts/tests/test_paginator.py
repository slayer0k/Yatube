from math import ceil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.TEST_OBJECTS = 16
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='test description'
        )
        cls.user = User.objects.create_user(username='leo')
        for number in range(cls.TEST_OBJECTS):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'test text {number}'
            )

    def setUp(self) -> None:
        self.client = Client()
        caches['default'].clear()

    def test_paginator_first_page(self):
        '''проверка первой страницы Paginator и объектов в него входящих'''
        url_tuple = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.post.group.slug,)),
            reverse('posts:profile', args=(self.post.author.username,))
        )
        for url in url_tuple:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.context['page_obj'].end_index(),
                    min(settings.LIMIT, self.TEST_OBJECTS)
                )

    def test_paginator_last_page(self):
        '''Проверка второй страницы Paginator'''
        url_tuple = (
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.post.group.slug,)),
            reverse('posts:profile', args=(self.post.author.username,))
        )
        page = ceil(self.TEST_OBJECTS / settings.LIMIT)
        for url in url_tuple:
            with self.subTest(url=url):
                response = self.client.get(
                    url + f'?page={page}'
                )
                self.assertEqual(
                    len(response.context['page_obj']),
                    (self.TEST_OBJECTS
                     - (settings.LIMIT * (page - 1))))
