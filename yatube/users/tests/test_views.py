from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class UsersPagesTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_signup_form_context(self):
        response = self.client.get(reverse('users:signup'))
        self.assertIsInstance(response.context['form'], CreationForm)
