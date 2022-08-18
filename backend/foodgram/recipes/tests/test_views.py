from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Ingredient, IngredientInRecipe, Recipe, Tag, TagInRecipe
from ..serializers import IngredientSerializer, TagSerializer
from users.models import User
from users.serializers import UserSerializer


class TagTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.breakfast_tag = Tag.objects.create(
            name='Завтрак',
            color='#ebff38',
            slug='breakfast'
        )
        cls.new_tag = Tag.objects.create(
            name='Новинка',
            color='#e3160b',
            slug='new'
        )

    def setUp(self):
        self.client = APIClient()

    def test_list_tags(self):
        """Проверяем способность API возвращать все тэги списком."""
        response = self.client.get(
            reverse('recipes:tags-list')
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2)

    def test_retrieve_tag(self):
        """Проверяем способность API возвращать один конкретный
        тэг по его первичному ключу."""
        response = self.client.get(
            reverse('recipes:tags-detail', kwargs={'id': 1})
        )
        tag = Tag.objects.get(pk=1)
        serializer = TagSerializer(tag)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_404_retrieve_tag(self):
        """Проверяем способность API возвращать ошибку 404 на запрос
        несуществующего тэга."""
        response = self.client.get(
            reverse('recipes:tags-detail', kwargs={'id': 100})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)


class IngredientTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.eggs = Ingredient.objects.create(
            name='Яйцо',
            measurement_unit='шт.'
        )

        cls.sausages = Ingredient.objects.create(
            name='Сосиска',
            measurement_unit='шт.'
        )

    def setUp(self):
        self.client = APIClient()

    def test_list_ingredients(self):
        """Проверяем способность API возвращать список
        всех ингредиентов."""
        response = self.client.get(
            reverse('recipes:ingredients-list')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_ingredients(self):
        """Проверяем способность API возвращать один конкретный
        ингредиент по его первичному ключу."""
        response = self.client.get(
            reverse('recipes:ingredients-detail', kwargs={'id': 2})
        )
        sausage = Ingredient.objects.get(pk=2)
        serializer = IngredientSerializer(sausage)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_filter_ingredients(self):
        """Проверим способность API возвращать лист ингредиентов,
        отфильтрованных по названию ингредиента."""

        urls = {
            'http://127.0.0.1:8000/api/ingredients/?name=Я': 1,
            'http://127.0.0.1:8000/api/ingredients/?name=Со': 1,
            'http://127.0.0.1:8000/api/ingredients/?name=си': 0,
        }

        for url, amount in urls.items():
            response = self.client.get(
                url,
                follow=True
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), amount)


class RecipeTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.retrieve_id_user = 1

        cls.russian_president = User.objects.create_user(
            username='v.putin',
            email='vlad.putin@mail.ru',
            first_name='Vladimir',
            last_name='Putin',
            password='RUSSIAN_FEDERATION'
        )
        cls.american_president = User.objects.create_user(
            username='j.biden',
            email='j.biden@gmail.ru',
            first_name='Joe',
            last_name='Biden',
            password='AMERICA'
        )

        cls.client = APIClient()

        cls.authenticated_client = APIClient()
        cls.authenticated_client.force_authenticate(cls.russian_president)

        cls.authenticated_client2 = APIClient()
        cls.authenticated_client2.force_authenticate(cls.american_president)

        cls.dumplings = Ingredient.objects.create(
            name='Пельмени',
            measurement_unit='г'
        )
        cls.egg = Ingredient.objects.create(
            name='Яйцо',
            measurement_unit='шт'
        )
        cls.sausage = Ingredient.objects.create(
            name='Сосиска',
            measurement_unit='шт'
        )

        cls.breakfast_tag = Tag.objects.create(
            name='Завтрак',
            color='#ebff38',
            slug='breakfast'
        )
        cls.new_tag = Tag.objects.create(
            name='Новинка',
            color='#e3160b',
            slug='new'
        )

        cls.recipe1 = Recipe.objects.create(
            author=cls.russian_president,
            name='Варенные пельмени',
            image='recipes/63fb3d69-37e1-4832-965d-fb282d1e8ba4.jpeg',
            text='Опускаем пельмени в кипящую подсоленную воду. Варим до готовности. Добавляем сметану по желанию.',
            cooking_time=12
        )

        cls.recipe1.ingredients.add(
            cls.dumplings,
            through_defaults={'amount': 300}
        )

        cls.recipe1.tags.add(cls.breakfast_tag)
        cls.recipe1.tags.add(cls.new_tag)

        cls.recipe2 = Recipe.objects.create(
            author=cls.american_president,
            name='Яичница с сосисками',
            image='recipe/yaichnica-s-sosiskami-770x513.jpeg',
            text='Нарезать сосиски, обжарить на среднем огне, залит яйцами.',
            cooking_time=10
        )

        cls.recipe2.ingredients.add(
            cls.egg,
            through_defaults={'amount': 3}
        )
        cls.recipe2.ingredients.add(
            cls.sausage,
            through_defaults={'amount': 2}
        )

    def test_list_recipes(self):
        response = self.client.get(reverse('recipes:recipes-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_filter_author_recipes(self):
        urls = {
            'http://127.0.0.1:8000/api/recipes/?author=1': 1,
            'http://127.0.0.1:8000/api/recipes/?author=2': 1,
        }
        for url, cnt in urls.items():
            response = self.client.get(
                url,
                follow=True
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['count'], cnt)

    def test_retrieve_status_code_recipes(self):
        response = self.client.get(
            reverse('recipes:recipes-detail',
                    kwargs={'pk': self.retrieve_id_user})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_in_recipes(self):
        """Проверяем возможность API отдавать корректную
        информацию по автору рецепта."""
        response = self.client.get(
            reverse('recipes:recipes-detail',
                    kwargs={'pk': 1})
        )

        user = User.objects.get(pk=self.russian_president.id)
        user_serializer = UserSerializer(user)
        self.assertEqual(user_serializer.data, response.data['author'])

    def test_retrieve_tags_in_recipes(self):
        """Проверяем возможность API отдавать корректные
        теги при запросе конкретного рецепта."""
        response = self.client.get(
            reverse('recipes:recipes-detail',
                    kwargs={'pk': 1})
        )
        tags = self.recipe1.tags_in.all()
        self.assertEqual(len(response.data['tags']), len(tags))

        for i in range(len(tags)):
            with self.subTest(tag=tags[i]):
                t = Tag.objects.get(pk=tags[i].tag_id)
                tag_serializer = TagSerializer(t)
                self.assertEqual(response.data['tags'][i], tag_serializer.data)

