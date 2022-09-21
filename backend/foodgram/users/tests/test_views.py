from django.urls import reverse
import json
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Subscription, User
from ..serializers import UserSerializer

from recipes.models import Recipe


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
        некорректные входные данные при попытке сменить пароль
        текущего пользователя."""
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


class SubscriptionTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = APIClient()

        cls.test_user = User.objects.create_user(
            username='test_username',
            email='test_user_email@yandex.ru',
            first_name='TestName',
            last_name='TestLastName',
            password='test_password1'
        )
        cls.authorized_user = APIClient()
        cls.authorized_user.force_authenticate(cls.test_user)

        cls.test_user2 = User.objects.create_user(
            username='test_username2',
            email='test_user_email2@yandex.ru',
            first_name='TestName2',
            last_name='TestLastName2',
            password='test_password2'
        )
        cls.authorized_user2 = APIClient()
        cls.authorized_user2.force_authenticate(cls.test_user2)

        cls.test_user3 = User.objects.create_user(
            username='test_username3',
            email='test_user_email3@yandex.ru',
            first_name='TestName3',
            last_name='TestLastName3',
            password='test_password3'
        )
        cls.authorized_user3 = APIClient()
        cls.authorized_user3.force_authenticate(cls.test_user3)

        cls.test_user4 = User.objects.create_user(
            username='test_username4',
            email='test_user_email4@yandex.ru',
            first_name='TestName4',
            last_name='TestLastName4',
            password='test_password4'
        )
        cls.authorized_user4 = APIClient()
        cls.authorized_user4.force_authenticate(cls.test_user4)

        cls.test_recipe1 = Recipe.objects.create(
            author=cls.test_user3,
            name='test recipe',
            image='recipes/63fb3d69-37e1-4832-965d-fb282d1e8ba4.jpeg',
            text='test text',
            cooking_time=5
        )
        cls.test_recipe2 = Recipe.objects.create(
            author=cls.test_user3,
            name='test recipe2',
            image='recipes/63fb3d69-37e1-4832-965d-fb282d1e8ba4.jpeg',
            text='test text2',
            cooking_time=10
        )

    def setUp(self):
        self.subscription2 = Subscription.objects.create(
            author=self.test_user2,
            subscriber=self.test_user
        )
        self.subscription3 = Subscription.objects.create(
            author=self.test_user3,
            subscriber=self.test_user
        )
        self.subscription4 = Subscription.objects.create(
            author=self.test_user4,
            subscriber=self.test_user
        )

    def test_create_subscription(self):
        """Проверяем возможность API создавать подписку одного
        пользователя на другого."""
        len_before = len(Subscription.objects.all())
        response = self.authorized_user2.post(
            reverse('users:users-subscribe', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        len_after = len(Subscription.objects.all())
        self.assertEqual(len_after, len_before + 1)

        for field in ['email', 'id', 'username', 'first_name', 'last_name',
                      'is_subscribed', 'recipes', 'recipes_count']:
            with self.subTest(field=field):
                self.assertIn(field, response.data.keys())

    def test_create_self_subscription(self):
        """Проверяем возможность API выдавать правильный ответ на
        запрос создания подписки на самого себя."""
        response = self.authorized_user.post(
            reverse('users:users-subscribe', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_double_subscription(self):
        """Проверяем возможность API выдавать правильный ответ на запрос
        создания повторной подписки на другого пользователя."""
        response = self.authorized_user.post(
            reverse('users:users-subscribe', kwargs={'id': 2})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unauthorized_subscription(self):
        """Проверяем возможность API отказывать в доступе неавторизованному
        пользователю на запрос создания подписки на пользователя."""
        response = self.user.post(
            reverse('users:users-subscribe', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_no_author_instance_subscription(self):
        """Проверяем возможность API возвращать правильный ответ на запрос
        создания подписки на несуществующего пользователя."""
        response = self.authorized_user2.post(
            reverse('users:users-subscribe', kwargs={'id': 100})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_subscription(self):
        """Проверяем возможность API удалять подписку."""
        len_before = len(Subscription.objects.all())
        response = self.authorized_user.delete(
            reverse('users:users-subscribe', kwargs={'id': 2})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        len_after = len(Subscription.objects.all())
        self.assertEqual(len_before, len_after + 1)

    def test_delete_no_subscription(self):
        """Проверяем возможность API правильно реагировать за запрос
        удаления подписки, которой нет у пользователя."""
        response = self.authorized_user2.delete(
            reverse('users:users-subscribe', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_self_subscription(self):
        """Проверяем возможность API выдавать правильный ответ на
        запрос удаления подписки на самого себя."""
        response = self.authorized_user.delete(
            reverse('users:users-subscribe', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_unauthorized_subscription(self):
        """Проверяем возможность API отказывать в доступе неавторизованному
        пользователю на запрос удаления подписки на пользователя."""
        response = self.user.delete(
            reverse('users:users-subscribe', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_no_user_instance_subscription(self):
        """Проверяем возможность API правильно реагировать на запрос
        удаления подписки на пользователя, которого не существует."""
        response = self.authorized_user.delete(
            reverse('users:users-subscribe', kwargs={'id': 100})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_subscriptions(self):
        """Проверяем возможность API возвращать все подписки
        текущего пользователя."""
        response = self.authorized_user.get(
            reverse('users:users-subscriptions')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_unauthorized_subscription(self):
        """Проверяем возможность API отказывать в доступе неавторизованному
        пользователю на запрос вывода всех подписок пользователя."""
        response = self.user.get(
            reverse('users:users-subscriptions')
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
