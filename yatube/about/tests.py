from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticPagesURLViewTests(TestCase):

    def setUp(self) -> None:
        self.geust_client = Client()

    def test_about_namespaces(self):
        '''Проверка доступности адресов приложения about'''
        url_names = (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/')
        )
        for name, url in url_names:
            with self.subTest(url=url):
                self.assertEqual(reverse(name), url)

    def test_template_exists(self):
        '''Проверка доступности шаблонов на месте'''
        template_url_names = (
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech')),
        )
        for template, url in template_url_names:
            with self.subTest(url=url):
                response = self.geust_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_page_accesible_by_name(self):
        '''URL, для страниц /about/author-tech доступен'''
        url_tuple = (
            reverse('about:author'),
            reverse('about:tech')
        )
        for url in url_tuple:
            with self.subTest(url=url):
                response = self.geust_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
