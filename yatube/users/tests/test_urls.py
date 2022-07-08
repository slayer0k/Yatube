from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(username='Mao')
        self.autorized_client = Client()
        self.autorized_client.force_login(self.user)

    def test_users_pages_namespace(self):
        url_reverse = (
            ('/auth/password_change/', reverse('users:password_change')),
            ('/auth/password_change/done/',
             reverse('users:password_change_done')),
            (
                '/auth/reset/Mw/61t-4fc97ac3b5fb58938cc8',
                reverse(
                    'users:reset_confirm',
                    args=('Mw', '61t-4fc97ac3b5fb58938cc8',)
                )
            ),
            ('/auth/logout/', reverse('users:logout')),
            ('/auth/signup/', reverse('users:signup')),
            ('/auth/login/', reverse('users:login')),
            ('/auth/password_reset/', reverse('users:password_reset')),
            ('/auth/password_reset/done/',
             reverse('users:password_reset_done')),
            ('/auth/reset/done/', reverse('users:reset_complete'))
        )
        for url, reverse_url in url_reverse:
            with self.subTest(url=url):
                self.assertEqual(reverse_url, url)

    def test_signup_page_access(self):
        response = self.client.get(
            reverse('users:signup')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_templates(self):
        templates = (
            (
                reverse(
                    'users:reset_confirm',
                    args=('Mw', '61t-4fc97ac3b5fb58938cc8',)),
                'users/password_reset_confirm.html'
            ),
            (
                reverse('users:password_change'),
                'users/password_change_form.html'
            ),
            (
                reverse('users:password_change_done'),
                'users/password_change_done.html'
            ),
            (reverse('users:signup'), 'users/signup.html'),
            (reverse('users:logout'), 'users/logged_out.html'),
            (reverse('users:login'), 'users/login.html'),
            (
                reverse('users:password_reset'),
                'users/password_reset_form.html'
            ),
            (
                reverse('users:password_reset_done'),
                'users/password_reset_done.html'
            ),
            (
                reverse('users:reset_complete'),
                'users/password_reset_complete.html'
            ),
        )
        for url, template in templates:
            with self.subTest(url=url):
                response = self.autorized_client.get(url)
                self.assertTemplateUsed(response, template)
