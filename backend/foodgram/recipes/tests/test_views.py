from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Tag
from ..serializers import TagSerializer


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
        response = self.client.get(
            reverse('recipes:tags-list')
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2)

    def test_retrieve_tag(self):
        response = self.client.get(
            reverse('recipes:tags-detail', kwargs={'pk': 1})
        )
        tag = Tag.objects.get(pk=1)
        serializer = TagSerializer(tag)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertTrue(len(response.data.get('color')) <= 7)
        self.assertTrue(len(response.data.get('slug')) <= 200)

