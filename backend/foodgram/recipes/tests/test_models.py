from django.test import TestCase

from ..models import Ingredient, Tag


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.breakfast_tag = Tag.objects.create(
            name='Завтрак',
            color='#ebff38',
            slug='breakfast'
        )

        cls.egg = Ingredient.objects.create(
            name='Яйцо',
            measurement_unit='шт.'
        )

        cls.object_list = [
            cls.breakfast_tag,
            cls.egg,
        ]

        cls.verbose_fields = {
            cls.breakfast_tag: {
                'name': 'Название тэга',
                'color': 'Цвет',
                'slug': 'slug'
            },
            cls.egg: {
                'name': 'Название ингредиента',
                'measurement_unit': 'Единица измерения'
            }
        }

    def test_verbose_name(self):
        """Проверяем, что поля модели имеют читаемые названия."""
        for model_object, fields in self.verbose_fields.items():
            for field, expected_value in fields.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        model_object._meta.get_field(field).verbose_name,
                        expected_value
                    )

    def test_object_name(self):
        """Проверяем, что объект модели имеет читаемое название."""
        for item in self.object_list:
            self.assertEqual(str(item), item.name)
