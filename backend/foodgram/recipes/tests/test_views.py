from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Ingredient, Tag
from ..serializers import IngredientSerializer, TagSerializer


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
