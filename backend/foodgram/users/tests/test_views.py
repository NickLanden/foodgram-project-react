from django.urls import reverse
import json
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import User
from ..serializers import UserSerializer


class GetUsers(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.potter = User.objects.create_user(
            username='h.potter',
            email='h.potter@hogwarts.com',
            first_name='Harry',
            last_name='Potter',
            password='JamesPotter'
        )
        cls.weasley = User.objects.create_user(
            username='r.weasley',
            email='r.weasley@hogwarts.com',
            first_name='Ron',
            last_name='Weasley',
            password='Cupcakes'
        )
        cls.granger = User.objects.create_user(
            username='h.granger',
            email='h.granger@hogwarts.com',
            first_name='Hermione',
            last_name='Granger',
            password='Books'
        )

    def setUp(self):
        self.client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(self.potter)

    def test_get_all_users(self):
        """Проверяем способность API возвращать всех пользователей"""
        response = self.client.get(reverse('users:users-list'))
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        self.assertEqual(response.data.get('results'), serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_success_single_user(self):
        """Проверяем способность API возвращать конкретного
        пользователей авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('users:users-detail', kwargs={'id': 3})
        )
        user = User.objects.get(pk=3)
        serializer = UserSerializer(user)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_authorizer_single_user(self):
        """Проверяем способность API возвращать ошибку неавторизованному
        пользователю при запросе конкретного пользователя."""
        response = self.client.get(
            reverse('users:users-detail', kwargs={'id': 3})
        )
        self.assertIn('detail', response.data)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_get_not_found_object_single_user(self):
        """Проверяем способность API возвращать ошибку
        на запрос несуществующего пользователя."""
        response = self.authorized_client.get(
            reverse('users:users-detail', kwargs={'id': 33})
        )
        self.assertIn('detail', response.data)
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_get_me_authorized_user(self):
        """Проверяем способность API возвращать
        данные по текущему авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('users:users-me')
        )
        me_user = User.objects.get(pk=1)
        serializer = UserSerializer(me_user)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_me_unauthorized_user(self):
        """Проверяем способность API возвращать ошибку
        неавторизованному пользователю при запросе
        данных о текущем пользователе."""
        response = self.client.get(
            reverse('users:users-me')
        )
        self.assertIn('detail', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CreateUserTest(APITestCase):
    def setUp(self):
        self.valid_payload = {
            "email": "test_email@yandex.ru",
            "username": "test_username",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "password": "test_password"
        }
        self.invalid_payload = {
            "username": "",
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "password": "test_password"
        }

    def test_create_valid_user(self):
        """Проверяем способность API регистрировать пользователя
        с использованием корректных входных данных."""
        response = self.client.post(
            reverse('users:users-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_user(self):
        """Проверяем способность API возвращать ошибку при получении
        некорректных данных при запросе на создание нового пользователя."""
        response = self.client.post(
            reverse('users:users-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordUserTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_username',
            email='test_user_email@yandex.ru',
            first_name='TestName',
            last_name='TestLastName',
            password='test_password1'
        )

    def setUp(self):
        self.client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(self.user)

        self.valid_payload = {
            'new_password': 'test_password2',
            'current_password': 'test_password1'
        }

        self.invalid_payload = {
            'new_password': 'test_password2'
        }

    def test_change_password_valid_user(self):
        """Проверяем способность API изменять пароль текущего пользователя."""
        response = self.authorized_client.post(
            reverse('users:users-set-password'),
            self.valid_payload
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password_invalid_user(self):
        """Проверяем способность API реагировать верным образом на
        некорректные входные данные при попытке сменить пароль текущего пользователя."""
        response = self.authorized_client.post(
            reverse('users:users-set-password'),
            self.invalid_payload
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthorized_user(self):
        """Проверяем способность API возвращать ошибку неавторизованному
        пользователю при запросе на изменение пароля."""
        response = self.client.post(
            reverse('users:users-set-password'),
            self.valid_payload
        )
        self.assertIn('detail', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenUserTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='test_username',
            email='test_user_email@yandex.ru',
            first_name='TestName',
            last_name='TestLastName',
            password='test_password1'
        )

    def setUp(self):
        self.client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(self.user)

        self.valid_payload = {
            'password': 'test_password1',
            'email': 'test_user_email@yandex.ru'
        }

        self.invalid_payload = {
            'password': 'test_password1',
            'email': 'test_email@yandex.ru'
        }

    def test_token_login_valid_user(self):
        """Проверяем способность API выдавать токены по адресу
        электронной почты и паролю."""
        response = self.authorized_client.post(
            reverse('users:login'),
            self.valid_payload
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('auth_token', response.data)

    def test_token_login_invalid_user(self):
        """Проверяем способность API выдавать ошибки при запросе
        токена с некорректными данными."""
        response = self.authorized_client.post(
            reverse('users:login'),
            self.invalid_payload
        )
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_token_logout_user(self):
        """Проверяем способность API удалять токен текущего пользователя."""
        response = self.authorized_client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_token_logout_unauthorized_user(self):
        """Проверяем способность API выдавать корректную ошибку
        при попытке удалить токен."""
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
