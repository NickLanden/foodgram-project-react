from django.test import TestCase

from ..models import User


class UserModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='new_test_user',
            email='new_test_user@yandex.ru',
            password='new_test_user',
            first_name='test_name',
            last_name='test_last_name'
        )
        cls.admin_user = User.objects.create_user(
            username='admin_username',
            email='admin@yandex.ru',
            password='admin_password',
            first_name='admin_name',
            last_name='admin_last_name',
            role='admin'
        )

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        user = UserModelTest.user
        fields_verboses = {
            'username': 'Имя пользователя',
            'email': 'Адрес электронной почты',
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }
        for field, expected_value in fields_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    user._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_model_has_correct_object_name(self):
        """Проверяем, что у моделей корректно работает __str__."""
        user = UserModelTest.user
        self.assertEqual(str(user), user.username)

    def test_is_user_attribute(self):
        """Проверяем свойство is_user на корректность работы."""
        self.assertEqual(self.user.is_user, True)
        self.assertEqual(self.admin_user.is_user, False)

    def test_is_admin_attribute(self):
        """Проверяем свойство is_admin на корректность работы."""
        self.assertEqual(self.admin_user.is_admin, True)
        self.assertEqual(self.user.is_admin, False)
