from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateFormTest(TestCase):
    def setUp(self) -> None:
        self.geust_client = Client()

    def test_signup_form(self):
        '''проверка добавления нового пользователя'''
        user_count = User.objects.count()
        form_date = {
            'first_name': 'Val',
            'last_name': 'Lobik',
            'username': 'Valobik',
            'email': 'val@lobik.com',
            'password1': '6f%5%sOC',
            'password2': '6f%5%sOC'

        }
        response = self.geust_client.post(
            reverse('users:signup'),
            data=form_date,
            follow=True
        )
        self.assertTrue(
            User.objects.filter(
                first_name=form_date['first_name'],
                last_name=form_date['last_name'],
                username=form_date['username'],
                email=form_date['email']
            )
        )
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
