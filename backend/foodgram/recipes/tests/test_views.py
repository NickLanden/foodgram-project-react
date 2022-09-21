from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
import json

from ..models import (Favorite, Ingredient,
                      Recipe, ShoppingCart, Tag)
from ..serializers import (IngredientSerializer,
                           IngredientInRecipeSerializer,
                           TagSerializer)
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
        url = 'http://127.0.0.1:8000/api/ingredients/'
        param = 'name'
        values = ['Я', 'Со', 'си']

        all_ingredients = Ingredient.objects.all()

        for i in values:
            with self.subTest(value=i):
                response = self.client.get(
                    f'{url}?{param}={i}',
                    follow=True
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    len(response.data),
                    len(all_ingredients.filter(name__startswith=i))
                )


class RecipeTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
            text=('Опускаем пельмени в кипящую подсоленную воду. '
                  'Варим до готовности. Добавляем сметану по желанию.'),
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
                    kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_in_recipes(self):
        """Проверяем возможность API отдавать корректную
        информацию по автору рецепта."""
        response = self.client.get(
            reverse('recipes:recipes-detail',
                    kwargs={'id': 1})
        )

        user = User.objects.get(pk=self.russian_president.id)
        user_serializer = UserSerializer(user)
        self.assertEqual(user_serializer.data, response.data['author'])

    def test_retrieve_tags_in_recipes(self):
        """Проверяем возможность API отдавать корректные
        теги при запросе конкретного рецепта."""
        response = self.client.get(
            reverse('recipes:recipes-detail',
                    kwargs={'id': 1})
        )
        tags = self.recipe1.tags_in.all()
        self.assertEqual(len(response.data['tags']), len(tags))

        for i in range(len(tags)):
            with self.subTest(tag=tags[i]):
                t = Tag.objects.get(pk=tags[i].tag_id)
                tag_serializer = TagSerializer(t)
                self.assertEqual(response.data['tags'][i],
                                 tag_serializer.data)

    def test_retrieve_ingredients_in_recipes(self):
        """Проверяем возможность API отдавать корректные
        ингредиенты при запросе конкретного рецепта."""
        response = self.client.get(
            reverse('recipes:recipes-detail',
                    kwargs={'id': 1})
        )
        ingredients = self.recipe1.ingredients_in.all()
        self.assertEqual(len(response.data['ingredients']),
                         len(ingredients))
        for i in range(len(ingredients)):
            with self.subTest(ingredient=ingredients[i]):
                ing_serializer = IngredientInRecipeSerializer(ingredients[i])
                self.assertEqual(response.data['ingredients'][i],
                                 ing_serializer.data)


class CreateRecipeTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.matroskin = User.objects.create_user(
            username='c.matroskin',
            email='cat.matroskin@mail.ru',
            first_name='Cat',
            last_name='Matroskin',
            password='milk'
        )
        cls.pechkin = User.objects.create_user(
            username='postman.pechkin',
            email='postman.pechkin@yandex.ru',
            first_name='postman',
            last_name='pechkin',
            password='bicycle'
        )

        cls.client = APIClient()

        cls.authenticated_client = APIClient()
        cls.authenticated_client.force_authenticate(cls.matroskin)

        cls.authenticated_client2 = APIClient()
        cls.authenticated_client2.force_authenticate(cls.pechkin)

        cls.doshirak = Ingredient.objects.create(
            name='Доширак',
            measurement_unit='шт'
        )
        cls.sour = Ingredient.objects.create(
            name='Сметана',
            measurement_unit='г'
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

        cls.doshirak_payload = {
            "tags": [
                1,
                2
            ],
            "ingredients": [
                {"id": 1, "amount": 1},
                {"id": 2, "amount": 100}
            ],
            "name": "Доширак",
            "text": "Заливаем кипятком и ждем 7 минут. Приятного аппетита!",
            "cooking_time": 7
        }

        cls.update_payload = {
            "tags": [
                1
            ],
            "ingredients": [
                {"id": 1, "amount": 1}
            ],
            "name": "Сосисочная яичница",
            "text": ("Нарезать сосиски, обжарить на "
                     "среднем огне, залит яйцами."),
            "cooking_time": 7
        }

        cls.update_payload2 = {
            "tags": [
                1,
                2
            ],
            "ingredients": [
                {"id": 1, "amount": 10},
                {"id": 2, "amount": 500}
            ],
            "name": "Сосисочная яичница",
            "text": ("Нарезать сосиски, обжарить на "
                     "среднем огне, залит яйцами."),
            "cooking_time": 7
        }

        cls.update_payload3 = {
            "tags": [
                1
            ],
            "ingredients": [
                {"id": 1, "amount": 10}
            ],
            "name": "Сосисочная яичница",
            "text": ("Нарезать сосиски, обжарить на "
                     "среднем огне, залит яйцами."),
            "cooking_time": 7
        }

        cls.recipe2 = Recipe.objects.create(
            author=cls.matroskin,
            name='Яичница с сосисками',
            image='recipe/yaichnica-s-sosiskami-770x513.jpeg',
            text='Нарезать сосиски, обжарить на среднем огне, залит яйцами.',
            cooking_time=10
        )

    def test_create_recipe(self):
        """Проверяем возможность API создавать объекты."""
        response = self.authenticated_client.post(
            reverse('recipes:recipes-list'),
            data=json.dumps(self.doshirak_payload),
            content_type='application/json'
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Recipe.objects.all()), 2)

        for field in ['id', 'tags', 'author', 'ingredients',
                      'is_favorited', 'is_in_shopping_cart',
                      'name', 'image', 'text', 'cooking_time']:
            with self.subTest(field=field):
                self.assertIn(field, response.data.keys())

    def test_delete_recipe(self):
        """Проверяем возможность API удалять рецепт"""
        response = self.authenticated_client.delete(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
        )
        deleted_recipe = Recipe.objects.all()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(deleted_recipe), 0)

    def test_delete_unauthorized_recipe(self):
        """Проверяем возможность API отказывать в доступе неавторизованным
        пользователям при запросе на удаление рецепта."""
        response = self.client.delete(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_author_recipe(self):
        """Проверяем возможность API запрещать удаление рецепта
        другого пользователя."""
        response = self.authenticated_client2.delete(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_recipe(self):
        """Проверяем возможность API обновлять рецепт."""
        response = self.authenticated_client.patch(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
            data=json.dumps(self.update_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'],
                         self.update_payload['name'])
        self.assertEqual(response.data['cooking_time'],
                         self.update_payload['cooking_time'])

        # Проверяем, что при обновлении рецепта могут
        # изменяться/добавляться экземпляры связанных моделей.
        response = self.authenticated_client.patch(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
            data=json.dumps(self.update_payload2),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tags']),
                         len(self.update_payload2['tags']))
        self.assertEqual(len(response.data['ingredients']),
                         len(self.update_payload2['ingredients']))
        self.assertEqual(response.data['ingredients'][0]['amount'],
                         self.update_payload2['ingredients'][0]['amount'])

        # Проверяем, что при обновлении рецепта могут
        # удаляться экземпляры связанных моделей.
        response = self.authenticated_client.patch(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
            data=json.dumps(self.update_payload3),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tags']),
                         len(self.update_payload3['tags']))
        self.assertEqual(len(response.data['ingredients']),
                         len(self.update_payload3['ingredients']))

    def test_update_unauthorized_recipe(self):
        response = self.client.patch(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
            data=json.dumps(self.update_payload3),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_not_author_recipe(self):
        response = self.authenticated_client2.patch(
            reverse('recipes:recipes-detail', kwargs={'id': 1}),
            data=json.dumps(self.update_payload3),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_no_object_recipe(self):
        response = self.authenticated_client.patch(
            reverse('recipes:recipes-detail', kwargs={'id': 100}),
            data=json.dumps(self.update_payload3),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FavoriteRecipeTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.ru',
            first_name='TestUserName',
            last_name='TestUserLastName',
            password='test_password'
        )
        cls.test_user2 = User.objects.create_user(
            username='test_user2',
            email='test_user2@gmail.ru',
            first_name='TestUser2Name',
            last_name='TestUser2LastName',
            password='test_password2'
        )

        cls.client = APIClient()

        cls.authenticated_client = APIClient()
        cls.authenticated_client.force_authenticate(cls.test_user)

        cls.authenticated_client2 = APIClient()
        cls.authenticated_client2.force_authenticate(cls.test_user2)

        cls.test_recipe = Recipe.objects.create(
            author=cls.test_user,
            name='test recipe',
            image='recipes/63fb3d69-37e1-4832-965d-fb282d1e8ba4.jpeg',
            text='test text',
            cooking_time=5
        )
        cls.test_recipe2 = Recipe.objects.create(
            author=cls.test_user,
            name='test recipe2',
            image='recipes/63fb3d69-37e1-4832-965d-fb282d1e8ba4.jpeg',
            text='test text2',
            cooking_time=5
        )

        cls.test_favorite = Favorite.objects.create(
            user=cls.test_user,
            recipe=cls.test_recipe2
        )

    def test_create_favorite(self):
        """Проверяем возможность API добавлять рецепты в избранное."""
        response = self.authenticated_client.post(
            reverse('recipes:recipes-favorite', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        favorite = Favorite.objects.filter(
            user=self.test_user, recipe=self.test_recipe)
        self.assertEqual(len(favorite), 1)

        for field in ['id', 'name', 'image', 'cooking_time']:
            with self.subTest(field=field):
                self.assertIn(field, response.data.keys())

    def test_create_duplicate_favorite(self):
        """Проверяем возможность API несколько раз добавлять
        один и тот же рецепт в избранное."""
        response = self.authenticated_client.post(
            reverse('recipes:recipes-favorite', kwargs={'id': 2})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unauthorized_favorite(self):
        """Проверяем возможность API отказывать в доступе при добавлении
        рецепта в избранное неавторизованным пользователем."""
        response = self.client.post(
            reverse('recipes:recipes-favorite', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_favorite(self):
        """Проверяем возможность API удалять рецепт из избранного."""
        response = self.authenticated_client.delete(
            reverse('recipes:recipes-favorite', kwargs={'id': 2})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_no_recipe_in_favorite(self):
        """Проверяем возможность API выдавать правильную ошибку на запрос
        удаления рецепта из избранного, который в избранном не находится."""
        response = self.authenticated_client.delete(
            reverse('recipes:recipes-favorite', kwargs={'id': 1})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_no_recipe_favorite(self):
        """Проверяем возможность API выдавать правильную ошибку на запрос
        удаления рецепта из избранного, которого не существует."""
        response = self.authenticated_client.delete(
            reverse('recipes:recipes-favorite', kwargs={'id': 100})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_unauthorized_favorite(self):
        """Проверяем возможность API отказывать в доступе при удалении
        рецепта из избранного неавторизованным пользователем."""
        response = self.client.delete(
            reverse('recipes:recipes-favorite', kwargs={'id': 2})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_author_favorite(self):
        """Проверяем возможность API отказывать в доступе при удалении
                рецепта из избранного неавторизованным пользователем."""
        response = self.authenticated_client2.delete(
            reverse('recipes:recipes-favorite', kwargs={'id': 2})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ShoppingCartTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = User.objects.create_user(
            username='test_user',
            email='test_user@gmail.ru',
            first_name='TestUserName',
            last_name='TestUserLastName',
            password='test_password'
        )
        cls.test_user2 = User.objects.create_user(
            username='test_user2',
            email='test_user2@gmail.ru',
            first_name='TestUser2Name',
            last_name='TestUser2LastName',
            password='test_password2'
        )

        cls.client = APIClient()

        cls.authenticated_client = APIClient()
        cls.authenticated_client.force_authenticate(cls.test_user)

        cls.authenticated_client2 = APIClient()
        cls.authenticated_client2.force_authenticate(cls.test_user2)

        cls.test_recipe = Recipe.objects.create(
            author=cls.test_user,
            name='test recipe',
            image='recipes/63fb3d69-37e1-4832-965d-fb282d1e8ba4.jpeg',
            text='test text',
            cooking_time=5
        )

    def setUp(self):
        self.shopping_cart = ShoppingCart.objects.create(
            user=self.test_user,
            recipe=self.test_recipe
        )

    def test_download_shopping_cart(self):
        """Проверяем возможность API возвращать список покупок файлом
        при соответствующем запросе."""
        response = self.authenticated_client2.get(
            reverse('recipes:recipes-download-shopping-cart')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_download_shopping_cart(self):
        """Проверяем возможность API отказывать неавторизованным
        пользователям скачивать список покупок."""
        response = self.client.get(
            reverse('recipes:recipes-download-shopping-cart')
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_shopping_cart(self):
        """Проверяем возможность API добавлять рецепт в список покупок."""
        response = self.authenticated_client2.post(
            reverse('recipes:recipes-shopping-cart',
                    kwargs={'id': self.test_recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for field in ['id', 'name', 'image', 'cooking_time']:
            with self.subTest(field=field):
                self.assertIn(field, response.data.keys())

    def test_create_no_recipe_shopping_cart(self):
        """Проверяем возможность API возвращать список покупок файлом
        при соответствующем запросе."""
        response = self.authenticated_client2.post(
            reverse('recipes:recipes-shopping-cart',
                    kwargs={'id': 100})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_double_recipe_in_shopping_cart(self):
        """Проверяем возможность API правильно реагировать при попытке
        добавить рецепт повторно в список покупок."""
        response = self.authenticated_client.post(
            reverse('recipes:recipes-shopping-cart',
                    kwargs={'id': self.test_recipe.id})
        )
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(len(response.data.keys()), 1)

    def test_create_unauthorized_shopping_cart(self):
        """Проверяем возможность API отказывать в доступе при
        попытке неавторизованного пользователя добавить рецепт
        в список покупок."""
        response = self.client.post(
            reverse('recipes:recipes-shopping-cart',
                    kwargs={'id': self.test_recipe.id})
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_shopping_cart(self):
        """Проверяем возможность API удалять по запросу рецепты
        из списка покупок."""
        cart_before = len(ShoppingCart.objects.all())
        response = self.authenticated_client.delete(
            reverse('recipes:recipes-shopping-cart',
                    kwargs={'id': self.test_recipe.id})
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT)

        cart_after = len(ShoppingCart.objects.all())
        self.assertEqual(cart_before, cart_after + 1)

    def test_delete_no_recipe_in_shopping_cart(self):
        """Проверяем возможность API правильно реагировать на запрос
        удаления рецепта из списка покупок, которого там нет."""
        response = self.authenticated_client2.delete(
            reverse('recipes:recipes-shopping-cart',
                    kwargs={'id': self.test_recipe.id})
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_unauthorized_shopping_cart(self):
        """Проверяем возможность API отказывать в доступе при
        попытке неавторизованного пользователя удалить рецепт
        из списка покупок."""
        response = self.client.delete(
            reverse('recipes:recipes-shopping-cart',
                    kwargs={'id': self.test_recipe.id})
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)
