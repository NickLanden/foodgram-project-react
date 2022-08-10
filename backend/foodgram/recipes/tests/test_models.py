from django.test import TestCase

from ..models import Tag


class TagModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.breakfast_tag = Tag.objects.create(
            name='Завтрак',
            color='#ebff38',
            slug='breakfast'
        )

    def test_verbose_name(self):
        """Проверяем, что поля модели тэгов имеют читаемые названия."""
        tag = self.breakfast_tag
        verbose_fields = {
            'name': 'Название тэга',
            'color': 'Цвет',
            'slug': 'slug'
        }
        for field, expected_value in verbose_fields.items():
            with self.subTest(field=field):
                self.assertEqual(
                    tag._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_object_name(self):
        """Проверяем, что объект модели тэгов имеет читаемое название."""
        tag = self.breakfast_tag
        self.assertEqual(str(tag), tag.name)
